from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole
from app.billing.models import OrderItem
from app.guests.models import Order

pytestmark = pytest.mark.asyncio(loop_scope="session")


def tenant_headers(restaurant_id: int, role: str = "manager") -> dict[str, str]:
    return {
        "x-test-restaurant-id": str(restaurant_id),
        "x-test-role": role,
    }


async def ensure_actor_user(db_session: AsyncSession, restaurant_id: int) -> None:
    existing = await db_session.execute(select(User).where(User.id == 999_999))
    if existing.scalar_one_or_none() is not None:
        return

    db_session.add(
        User(
            id=999_999,
            email="tenant-test@example.com",
            password_hash="test-hash",
            full_name="Tenant Test",
            role=UserRole.manager,
            is_active=True,
            restaurant_id=restaurant_id,
        )
    )
    await db_session.flush()


async def seed_demand_and_guest_history(db_session: AsyncSession, tenant_seed: Any) -> None:
    db_session.add(
        OrderItem(
            restaurant_id=tenant_seed.restaurant_a_id,
            order_id=tenant_seed.billing_order_a_id,
            menu_item_id=tenant_seed.menu_item_a_id,
            item_name="Menu A Hot",
            quantity=6,
            unit_price=12.5,
            total_price=75.0,
            status="served",
        )
    )
    db_session.add(
        Order(
            restaurant_id=tenant_seed.restaurant_a_id,
            guest_id=tenant_seed.guest_a_id,
            order_date=datetime.now(timezone.utc),
            channel="dine_in",
            total=42.0,
            discount=0,
            tip=0,
            items_json={"items": [{"name": "Menu A Hot", "qty": 1}]},
        )
    )
    await db_session.flush()


async def test_upsell_optimizer_personalized_with_expected_uplift(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)
    await seed_demand_and_guest_history(db_session, tenant_seed)

    response = await client.get(
        f"/api/agents/revenue-control-tower/upsell-candidates?guest_id={tenant_seed.guest_a_id}&limit=3",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["candidates"]) >= 1
    first = body["candidates"][0]
    assert first["expected_uplift"] >= 0
    assert first["guest_affinity_score"] > 0


async def test_experiment_lifecycle_and_uplift_dashboard(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    create = await client.post(
        "/api/agents/revenue-control-tower/experiments",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "name": "Dinner Price Test",
            "experiment_type": "price",
            "budget_cap": 100,
            "config_json": {
                "target_menu_item_id": tenant_seed.menu_item_a_id,
                "variants": [
                    {"key": "control", "price_multiplier": 1.0},
                    {"key": "treatment", "price_multiplier": 1.08},
                ],
                "max_price_change_pct": 15,
                "min_margin_pct": 5,
            },
        },
    )
    assert create.status_code == 201
    experiment_id = create.json()["id"]

    start = await client.post(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/start",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert start.status_code == 200
    assert start.json()["status"] == "running"

    for variant, exposures, conversions, revenue in [
        ("control", 100, 10, 500.0),
        ("treatment", 100, 13, 620.0),
    ]:
        rec = await client.post(
            f"/api/agents/revenue-control-tower/experiments/{experiment_id}/events",
            headers=tenant_headers(tenant_seed.restaurant_a_id),
            json={
                "variant_key": variant,
                "exposures": exposures,
                "conversions": conversions,
                "revenue_amount": revenue,
                "spend_amount": 10.0,
            },
        )
        assert rec.status_code == 200

    dashboard = await client.get(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/uplift-dashboard",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert dashboard.status_code == 200
    dashboard_json = dashboard.json()
    assert dashboard_json["control_variant"] == "control"
    assert len(dashboard_json["variants"]) >= 2
    assert dashboard_json["total_revenue"] >= 1120.0

    stop = await client.post(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/stop",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert stop.status_code == 200
    assert stop.json()["status"] == "stopped"


async def test_guardrails_and_budget_caps_enforced_per_tenant(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    policy_update = await client.put(
        "/api/agents/revenue-control-tower/policy",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "kill_switch": False,
            "daily_budget_cap": 5.0,
            "experiment_budget_cap": 3.0,
            "max_discount_pct": 20.0,
            "max_price_change_pct": 20.0,
            "min_margin_pct": 5.0,
        },
    )
    assert policy_update.status_code == 200

    bad_exp = await client.post(
        "/api/agents/revenue-control-tower/experiments",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "name": "Promo Over-Discount",
            "experiment_type": "promo",
            "config_json": {
                "target_menu_item_id": tenant_seed.menu_item_a_id,
                "variants": [{"key": "treatment", "promo_discount_pct": 35}],
            },
        },
    )
    assert bad_exp.status_code == 409

    good_exp = await client.post(
        "/api/agents/revenue-control-tower/experiments",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "name": "Promo Within Limits",
            "experiment_type": "promo",
            "budget_cap": 2.0,
            "config_json": {
                "target_menu_item_id": tenant_seed.menu_item_a_id,
                "variants": [
                    {"key": "control", "promo_discount_pct": 0},
                    {"key": "treatment", "promo_discount_pct": 10},
                ],
            },
        },
    )
    assert good_exp.status_code == 201
    experiment_id = good_exp.json()["id"]

    start = await client.post(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/start",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert start.status_code == 200

    ok_event = await client.post(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/events",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "variant_key": "treatment",
            "exposures": 10,
            "conversions": 2,
            "revenue_amount": 100,
            "spend_amount": 1.5,
        },
    )
    assert ok_event.status_code == 200

    cap_blocked = await client.post(
        f"/api/agents/revenue-control-tower/experiments/{experiment_id}/events",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={
            "variant_key": "treatment",
            "exposures": 10,
            "conversions": 2,
            "revenue_amount": 100,
            "spend_amount": 1.0,
        },
    )
    assert cap_blocked.status_code == 409

    kill_switch_on = await client.put(
        "/api/agents/revenue-control-tower/policy",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
        json={"kill_switch": True},
    )
    assert kill_switch_on.status_code == 200

    blocked_by_kill_switch = await client.get(
        "/api/agents/revenue-control-tower/upsell-candidates",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert blocked_by_kill_switch.status_code == 403
