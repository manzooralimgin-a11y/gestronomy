from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models import OrderItem
from app.core.models import (
    AgentAction,
    RevenueControlPolicy,
    RevenueExperiment,
    RevenueExperimentEvent,
    RevenueUpsellRecommendation,
)
from app.core.schemas import (
    RevenueControlPolicyRead,
    RevenueControlPolicyUpdate,
    RevenueExperimentCreate,
    RevenueExperimentDashboardResponse,
    RevenueExperimentEventCreate,
    RevenueExperimentRead,
    RevenueExperimentStopResponse,
    RevenueUpsellCandidate,
    RevenueUpsellOptimizerResponse,
)
from app.guests.models import GuestProfile, Order
from app.menu.models import MenuItem
from app.shared.audit import emit_sensitive_audit, log_human_action
from app.inventory.models import InventoryItem

REVENUE_AGENT_NAME = "RevenueControlTowerAgent"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {part for part in normalized.split() if len(part) >= 3}


async def _get_or_create_policy(db: AsyncSession, restaurant_id: int) -> RevenueControlPolicy:
    result = await db.execute(
        select(RevenueControlPolicy).where(RevenueControlPolicy.restaurant_id == restaurant_id)
    )
    policy = result.scalar_one_or_none()
    if policy is not None:
        return policy

    policy = RevenueControlPolicy(
        restaurant_id=restaurant_id,
        kill_switch=False,
        daily_budget_cap=500.0,
        experiment_budget_cap=200.0,
        max_discount_pct=30.0,
        max_price_change_pct=25.0,
        min_margin_pct=15.0,
        is_active=True,
    )
    db.add(policy)
    await db.flush()
    await db.refresh(policy)
    return policy


async def get_revenue_control_policy(
    db: AsyncSession, restaurant_id: int
) -> RevenueControlPolicyRead:
    policy = await _get_or_create_policy(db, restaurant_id)
    return RevenueControlPolicyRead.model_validate(policy)


async def update_revenue_control_policy(
    db: AsyncSession,
    restaurant_id: int,
    payload: RevenueControlPolicyUpdate,
    actor_user_id: int | None,
) -> RevenueControlPolicyRead:
    policy = await _get_or_create_policy(db, restaurant_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, key, value)
    await db.flush()
    await db.refresh(policy)

    await log_human_action(
        db,
        action="revenue_control_policy_updated",
        detail="Updated revenue control policy limits",
        entity_type="agents",
        entity_id=policy.id,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=actor_user_id,
    )
    emit_sensitive_audit(
        action="revenue_control_policy_updated",
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=REVENUE_AGENT_NAME,
        status="updated",
        detail="Updated revenue control policy",
        metadata=payload.model_dump(exclude_unset=True),
    )
    return RevenueControlPolicyRead.model_validate(policy)


async def _guest_affinity_score(
    db: AsyncSession, restaurant_id: int, guest_id: int | None, item_tokens: set[str]
) -> tuple[float, list[str]]:
    if guest_id is None:
        return 0.35, ["No guest selected: using baseline affinity."]

    guest_result = await db.execute(
        select(GuestProfile).where(
            GuestProfile.id == guest_id,
            GuestProfile.restaurant_id == restaurant_id,
        )
    )
    guest = guest_result.scalar_one_or_none()
    if guest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found")

    orders_result = await db.execute(
        select(Order).where(Order.restaurant_id == restaurant_id, Order.guest_id == guest_id).limit(50)
    )
    order_rows = list(orders_result.scalars().all())
    history_tokens: set[str] = set()
    for order in order_rows:
        items_json = order.items_json or {}
        items = items_json.get("items", []) if isinstance(items_json, dict) else []
        for row in items:
            if not isinstance(row, dict):
                continue
            history_tokens.update(_tokenize(str(row.get("name", ""))))

    flavor_tokens: set[str] = set()
    if isinstance(guest.flavor_profile_json, dict):
        for value in guest.flavor_profile_json.values():
            if isinstance(value, str):
                flavor_tokens.update(_tokenize(value))

    overlap_history = len(item_tokens & history_tokens)
    overlap_flavor = len(item_tokens & flavor_tokens)
    score = 0.3 + min(0.5, overlap_history * 0.12) + min(0.2, overlap_flavor * 0.08)
    score = max(0.1, min(1.0, score))

    reasons: list[str] = []
    if overlap_history:
        reasons.append("Matches guest order history.")
    if overlap_flavor:
        reasons.append("Matches guest flavor profile.")
    if not reasons:
        reasons.append("Low history overlap; candidate selected from demand signal.")
    return score, reasons


async def _demand_by_item(
    db: AsyncSession, restaurant_id: int, since: datetime
) -> dict[int, float]:
    demand_result = await db.execute(
        select(OrderItem.menu_item_id, func.sum(OrderItem.quantity))
        .where(
            OrderItem.restaurant_id == restaurant_id,
            OrderItem.created_at >= since,
        )
        .group_by(OrderItem.menu_item_id)
    )
    demand_rows = demand_result.all()
    if not demand_rows:
        return {}

    values = {int(menu_item_id): float(quantity or 0) for menu_item_id, quantity in demand_rows}
    peak = max(values.values()) or 1.0
    return {item_id: qty / peak for item_id, qty in values.items()}


async def _inventory_pressure_by_item(
    db: AsyncSession, restaurant_id: int, menu_items: list[MenuItem]
) -> dict[int, float]:
    inv_result = await db.execute(
        select(InventoryItem).where(InventoryItem.restaurant_id == restaurant_id)
    )
    inventory_items = list(inv_result.scalars().all())
    token_to_pressure: dict[str, float] = {}
    for inv in inventory_items:
        inv_tokens = _tokenize(inv.name)
        if not inv_tokens:
            continue
        ratio = 1.0
        if inv.par_level and inv.par_level > 0:
            ratio = float(inv.current_stock) / float(inv.par_level)
        pressure = max(0.0, min(1.0, 1.0 - ratio))
        for token in inv_tokens:
            token_to_pressure[token] = max(token_to_pressure.get(token, 0.0), pressure)

    out: dict[int, float] = {}
    for item in menu_items:
        item_tokens = _tokenize(item.name) | _tokenize(item.description)
        if not item_tokens:
            out[item.id] = 0.25
            continue
        matched = [token_to_pressure[token] for token in item_tokens if token in token_to_pressure]
        out[item.id] = max(matched) if matched else 0.25
    return out


async def optimize_upsell_candidates(
    db: AsyncSession,
    restaurant_id: int,
    guest_id: int | None,
    limit: int = 5,
) -> RevenueUpsellOptimizerResponse:
    policy = await _get_or_create_policy(db, restaurant_id)
    if policy.kill_switch:
        emit_sensitive_audit(
            action="revenue_experiment_create_blocked",
            tenant_id=restaurant_id,
            user_id=None,
            agent_id=REVENUE_AGENT_NAME,
            status="blocked",
            detail="Kill-switch enabled",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Revenue control kill-switch is enabled for this tenant",
        )

    items_result = await db.execute(
        select(MenuItem).where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True,
        )
    )
    menu_items = list(items_result.scalars().all())
    if not menu_items:
        return RevenueUpsellOptimizerResponse(
            generated_at=_now_utc(),
            guest_id=guest_id,
            candidates=[],
        )

    demand_map = await _demand_by_item(db, restaurant_id, _now_utc() - timedelta(days=14))
    inventory_pressure = await _inventory_pressure_by_item(db, restaurant_id, menu_items)

    scored: list[RevenueUpsellCandidate] = []
    for item in menu_items:
        item_tokens = _tokenize(item.name) | _tokenize(item.description)
        affinity_score, affinity_reasons = await _guest_affinity_score(
            db, restaurant_id, guest_id, item_tokens
        )
        demand_score = demand_map.get(item.id, 0.2)
        inventory_risk = inventory_pressure.get(item.id, 0.25)
        expected_uplift = max(
            0.0,
            float(item.price)
            * (0.02 + (demand_score * 0.05) + (affinity_score * 0.07) - (inventory_risk * 0.04)),
        )
        rationale = [
            f"Demand score {round(demand_score, 3)}",
            f"Inventory risk {round(inventory_risk, 3)}",
            f"Guest affinity {round(affinity_score, 3)}",
            *affinity_reasons,
        ]

        scored.append(
            RevenueUpsellCandidate(
                menu_item_id=item.id,
                item_name=item.name,
                base_price=float(item.price),
                demand_score=round(demand_score, 3),
                inventory_risk_score=round(inventory_risk, 3),
                guest_affinity_score=round(affinity_score, 3),
                expected_uplift=round(expected_uplift, 2),
                rationale=rationale,
            )
        )

    candidates = sorted(scored, key=lambda row: row.expected_uplift, reverse=True)[: max(1, limit)]
    generated_at = _now_utc()
    for row in candidates:
        db.add(
            RevenueUpsellRecommendation(
                restaurant_id=restaurant_id,
                guest_id=guest_id,
                generated_at=generated_at,
                menu_item_id=row.menu_item_id,
                expected_uplift=row.expected_uplift,
                factors_json={
                    "demand_score": row.demand_score,
                    "inventory_risk_score": row.inventory_risk_score,
                    "guest_affinity_score": row.guest_affinity_score,
                    "rationale": row.rationale,
                },
            )
        )

    db.add(
        AgentAction(
            agent_name=REVENUE_AGENT_NAME,
            action_type="upsell_optimizer",
            description="Generated personalized upsell candidates",
            input_data={"restaurant_id": restaurant_id, "guest_id": guest_id, "limit": limit},
            output_data={
                "candidates": [
                    {
                        "menu_item_id": row.menu_item_id,
                        "expected_uplift": row.expected_uplift,
                    }
                    for row in candidates
                ],
                "entity_type": "guests",
                "entity_id": guest_id,
            },
            status="suggested",
            confidence=0.78,
            requires_approval=False,
        )
    )

    await db.flush()
    return RevenueUpsellOptimizerResponse(
        generated_at=generated_at,
        guest_id=guest_id,
        candidates=candidates,
    )


def _extract_guardrail_config(config_json: dict | None) -> tuple[float, float, float]:
    config = config_json or {}
    return (
        float(config.get("max_discount_pct", 30.0)),
        float(config.get("max_price_change_pct", 25.0)),
        float(config.get("min_margin_pct", 15.0)),
    )


async def _validate_experiment_guardrails(
    db: AsyncSession,
    restaurant_id: int,
    policy: RevenueControlPolicy,
    experiment: RevenueExperiment,
) -> None:
    config = experiment.config_json or {}
    target_menu_item_id = config.get("target_menu_item_id")
    if target_menu_item_id is None:
        return

    item_result = await db.execute(
        select(MenuItem).where(
            MenuItem.id == int(target_menu_item_id),
            MenuItem.restaurant_id == restaurant_id,
        )
    )
    item = item_result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target menu item not found")

    max_discount_pct, max_price_change_pct, min_margin_pct = _extract_guardrail_config(config)
    max_discount_pct = min(max_discount_pct, float(policy.max_discount_pct))
    max_price_change_pct = min(max_price_change_pct, float(policy.max_price_change_pct))
    min_margin_pct = max(min_margin_pct, float(policy.min_margin_pct))

    base_price = float(item.price)
    cost = float(item.cost)
    variants = config.get("variants", [])
    if not isinstance(variants, list):
        variants = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue
        discount_pct = float(variant.get("promo_discount_pct", 0.0))
        if discount_pct > max_discount_pct:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Discount {discount_pct}% exceeds max guardrail {max_discount_pct}%",
            )

        multiplier = float(variant.get("price_multiplier", 1.0))
        price_change_pct = abs((multiplier - 1.0) * 100.0)
        if price_change_pct > max_price_change_pct:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Price change {price_change_pct}% exceeds max guardrail {max_price_change_pct}%",
            )

        new_price = base_price * multiplier * (1.0 - discount_pct / 100.0)
        if new_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Variant produces non-positive effective price",
            )
        margin_pct = ((new_price - cost) / new_price) * 100.0 if new_price > 0 else -999.0
        if margin_pct < min_margin_pct:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Variant margin {round(margin_pct, 2)}% below guardrail {min_margin_pct}%",
            )


async def _tenant_spend_today(db: AsyncSession, restaurant_id: int) -> float:
    start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    spend_result = await db.execute(
        select(func.coalesce(func.sum(RevenueExperimentEvent.spend_amount), 0.0)).where(
            RevenueExperimentEvent.restaurant_id == restaurant_id,
            RevenueExperimentEvent.recorded_at >= start,
            RevenueExperimentEvent.recorded_at < end,
        )
    )
    return float(spend_result.scalar() or 0.0)


async def create_revenue_experiment(
    db: AsyncSession,
    restaurant_id: int,
    payload: RevenueExperimentCreate,
    actor_user_id: int | None,
) -> RevenueExperimentRead:
    policy = await _get_or_create_policy(db, restaurant_id)
    if policy.kill_switch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Revenue control kill-switch is enabled for this tenant",
        )

    experiment = RevenueExperiment(
        restaurant_id=restaurant_id,
        name=payload.name,
        experiment_type=payload.experiment_type,
        status="draft",
        config_json=payload.config_json,
        budget_cap=payload.budget_cap,
        started_at=None,
        stopped_at=None,
    )
    db.add(experiment)
    await db.flush()
    await db.refresh(experiment)
    await _validate_experiment_guardrails(db, restaurant_id, policy, experiment)
    await db.flush()

    await log_human_action(
        db,
        action="revenue_experiment_created",
        detail=f"Created revenue experiment '{experiment.name}'",
        entity_type="agents",
        entity_id=experiment.id,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=actor_user_id,
    )
    emit_sensitive_audit(
        action="revenue_experiment_created",
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
        status="created",
        detail=f"Created experiment {experiment.id}",
        metadata={"experiment_type": experiment.experiment_type},
    )
    return RevenueExperimentRead.model_validate(experiment)


async def _get_experiment(
    db: AsyncSession, restaurant_id: int, experiment_id: int
) -> RevenueExperiment:
    result = await db.execute(
        select(RevenueExperiment).where(
            RevenueExperiment.id == experiment_id,
            RevenueExperiment.restaurant_id == restaurant_id,
        )
    )
    experiment = result.scalar_one_or_none()
    if experiment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    return experiment


async def start_revenue_experiment(
    db: AsyncSession,
    restaurant_id: int,
    experiment_id: int,
    actor_user_id: int | None,
) -> RevenueExperimentRead:
    policy = await _get_or_create_policy(db, restaurant_id)
    if policy.kill_switch:
        emit_sensitive_audit(
            action="revenue_experiment_start_blocked",
            tenant_id=restaurant_id,
            user_id=actor_user_id,
            agent_id=REVENUE_AGENT_NAME,
            status="blocked",
            detail="Kill-switch enabled",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Revenue control kill-switch is enabled for this tenant",
        )

    experiment = await _get_experiment(db, restaurant_id, experiment_id)
    await _validate_experiment_guardrails(db, restaurant_id, policy, experiment)

    tenant_spend_today = await _tenant_spend_today(db, restaurant_id)
    if tenant_spend_today >= float(policy.daily_budget_cap):
        emit_sensitive_audit(
            action="revenue_experiment_start_blocked",
            tenant_id=restaurant_id,
            user_id=actor_user_id,
            agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
            status="blocked",
            detail="Daily tenant budget cap reached",
            metadata={"tenant_spend_today": tenant_spend_today},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Daily tenant budget cap has already been reached",
        )

    experiment.status = "running"
    experiment.started_at = _now_utc()
    await db.flush()
    await db.refresh(experiment)
    await log_human_action(
        db,
        action="revenue_experiment_started",
        detail=f"Started revenue experiment '{experiment.name}'",
        entity_type="agents",
        entity_id=experiment.id,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=actor_user_id,
    )
    emit_sensitive_audit(
        action="revenue_experiment_started",
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
        status="started",
        detail=f"Started experiment {experiment.id}",
    )
    return RevenueExperimentRead.model_validate(experiment)


async def stop_revenue_experiment(
    db: AsyncSession,
    restaurant_id: int,
    experiment_id: int,
    actor_user_id: int | None,
) -> RevenueExperimentStopResponse:
    experiment = await _get_experiment(db, restaurant_id, experiment_id)
    experiment.status = "stopped"
    experiment.stopped_at = _now_utc()
    await db.flush()
    await db.refresh(experiment)
    await log_human_action(
        db,
        action="revenue_experiment_stopped",
        detail=f"Stopped revenue experiment '{experiment.name}'",
        entity_type="agents",
        entity_id=experiment.id,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=actor_user_id,
    )
    emit_sensitive_audit(
        action="revenue_experiment_stopped",
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
        status="stopped",
        detail=f"Stopped experiment {experiment.id}",
    )
    return RevenueExperimentStopResponse(
        experiment_id=experiment.id,
        status=experiment.status,
        stopped_at=experiment.stopped_at,
    )


async def record_revenue_experiment_event(
    db: AsyncSession,
    restaurant_id: int,
    experiment_id: int,
    payload: RevenueExperimentEventCreate,
    actor_user_id: int | None,
) -> RevenueExperimentRead:
    policy = await _get_or_create_policy(db, restaurant_id)
    if policy.kill_switch:
        emit_sensitive_audit(
            action="revenue_experiment_event_blocked",
            tenant_id=restaurant_id,
            user_id=actor_user_id,
            agent_id=REVENUE_AGENT_NAME,
            status="blocked",
            detail="Kill-switch enabled",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Revenue control kill-switch is enabled for this tenant",
        )

    experiment = await _get_experiment(db, restaurant_id, experiment_id)
    if experiment.status != "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experiment must be running before events can be recorded",
        )

    today_spend = await _tenant_spend_today(db, restaurant_id)
    if today_spend + payload.spend_amount > float(policy.daily_budget_cap):
        emit_sensitive_audit(
            action="revenue_experiment_event_blocked",
            tenant_id=restaurant_id,
            user_id=actor_user_id,
            agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
            status="blocked",
            detail="Daily tenant budget cap exceeded",
            metadata={"today_spend": today_spend, "incoming_spend": payload.spend_amount},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Daily tenant budget cap exceeded",
        )

    experiment_cap = float(experiment.budget_cap or policy.experiment_budget_cap)
    if float(experiment.spent_amount) + payload.spend_amount > experiment_cap:
        emit_sensitive_audit(
            action="revenue_experiment_event_blocked",
            tenant_id=restaurant_id,
            user_id=actor_user_id,
            agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
            status="blocked",
            detail="Experiment budget cap exceeded",
            metadata={
                "experiment_spent": float(experiment.spent_amount),
                "incoming_spend": payload.spend_amount,
                "experiment_cap": experiment_cap,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experiment budget cap exceeded",
        )

    event = RevenueExperimentEvent(
        restaurant_id=restaurant_id,
        experiment_id=experiment.id,
        variant_key=payload.variant_key,
        exposures=payload.exposures,
        conversions=payload.conversions,
        revenue_amount=payload.revenue_amount,
        spend_amount=payload.spend_amount,
        recorded_at=_now_utc(),
    )
    db.add(event)
    experiment.exposures += payload.exposures
    experiment.conversions += payload.conversions
    experiment.revenue_amount = float(experiment.revenue_amount) + payload.revenue_amount
    experiment.spent_amount = float(experiment.spent_amount) + payload.spend_amount
    await db.flush()
    await db.refresh(experiment)

    await log_human_action(
        db,
        action="revenue_experiment_event_recorded",
        detail=f"Recorded event for experiment '{experiment.name}' variant '{payload.variant_key}'",
        entity_type="agents",
        entity_id=experiment.id,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=actor_user_id,
    )
    emit_sensitive_audit(
        action="revenue_experiment_event_recorded",
        tenant_id=restaurant_id,
        user_id=actor_user_id,
        agent_id=f"{REVENUE_AGENT_NAME}:{experiment.id}",
        status="recorded",
        detail=f"Recorded event for experiment {experiment.id}",
        metadata={
            "variant_key": payload.variant_key,
            "exposures": payload.exposures,
            "conversions": payload.conversions,
            "revenue_amount": payload.revenue_amount,
            "spend_amount": payload.spend_amount,
        },
    )
    return RevenueExperimentRead.model_validate(experiment)


async def get_revenue_experiment_dashboard(
    db: AsyncSession, restaurant_id: int, experiment_id: int
) -> RevenueExperimentDashboardResponse:
    experiment = await _get_experiment(db, restaurant_id, experiment_id)
    events_result = await db.execute(
        select(RevenueExperimentEvent).where(
            RevenueExperimentEvent.restaurant_id == restaurant_id,
            RevenueExperimentEvent.experiment_id == experiment.id,
        )
    )
    events = list(events_result.scalars().all())

    by_variant: dict[str, dict[str, float]] = {}
    for event in events:
        row = by_variant.setdefault(
            event.variant_key,
            {"exposures": 0.0, "conversions": 0.0, "revenue": 0.0, "spend": 0.0},
        )
        row["exposures"] += float(event.exposures)
        row["conversions"] += float(event.conversions)
        row["revenue"] += float(event.revenue_amount)
        row["spend"] += float(event.spend_amount)

    variant_keys = sorted(by_variant.keys())
    if "control" in by_variant:
        control_key = "control"
    elif variant_keys:
        control_key = variant_keys[0]
    else:
        control_key = "control"
        by_variant[control_key] = {"exposures": 0.0, "conversions": 0.0, "revenue": 0.0, "spend": 0.0}

    control = by_variant[control_key]
    control_cr = (control["conversions"] / control["exposures"]) if control["exposures"] > 0 else 0.0
    control_rpe = (control["revenue"] / control["exposures"]) if control["exposures"] > 0 else 0.0

    variants = []
    for key in variant_keys or [control_key]:
        row = by_variant.get(key, {"exposures": 0.0, "conversions": 0.0, "revenue": 0.0, "spend": 0.0})
        cr = (row["conversions"] / row["exposures"]) if row["exposures"] > 0 else 0.0
        rpe = (row["revenue"] / row["exposures"]) if row["exposures"] > 0 else 0.0
        variants.append(
            {
                "variant_key": key,
                "exposures": int(row["exposures"]),
                "conversions": int(row["conversions"]),
                "conversion_rate": round(cr, 4),
                "revenue_amount": round(row["revenue"], 2),
                "spend_amount": round(row["spend"], 2),
                "revenue_per_exposure": round(rpe, 4),
                "conversion_uplift_vs_control_pct": round(((cr - control_cr) * 100.0), 2),
                "revenue_uplift_vs_control_per_exposure": round(rpe - control_rpe, 4),
            }
        )

    total_revenue = sum(float(row["revenue"]) for row in by_variant.values())
    total_spend = sum(float(row["spend"]) for row in by_variant.values())
    net_uplift = total_revenue - total_spend

    return RevenueExperimentDashboardResponse(
        experiment=RevenueExperimentRead.model_validate(experiment),
        control_variant=control_key,
        variants=variants,
        total_revenue=round(total_revenue, 2),
        total_spend=round(total_spend, 2),
        net_uplift=round(net_uplift, 2),
    )
