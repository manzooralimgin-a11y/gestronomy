from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models import OrderItem, TableOrder
from app.core.models import AgentAction, AgentConfig, ServiceAutopilotPrediction
from app.core.schemas import (
    PredictorAccuracy,
    ServiceAutopilotActionExecuteResponse,
    ServiceAutopilotPredictionResponse,
    ServiceAutopilotSuggestionRead,
    ServiceAutopilotSuggestResponse,
    TableDelayPrediction,
)
from app.reservations.models import Reservation, Table, TableSession
from app.shared.audit import emit_sensitive_audit, log_human_action

AUTOPILOT_AGENT_NAME = "ServiceAutopilotAgent"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _validate_horizon_minutes(horizon_minutes: int) -> None:
    if horizon_minutes < 5 or horizon_minutes > 60 or horizon_minutes % 5 != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="horizon_minutes must be between 5 and 60 in 5-minute increments",
        )


def _action_restaurant_id(action: AgentAction) -> int | None:
    if not action.input_data:
        return None
    restaurant_id = action.input_data.get("restaurant_id")
    if isinstance(restaurant_id, int):
        return restaurant_id
    return None


async def _get_or_create_agent_config(db: AsyncSession) -> AgentConfig:
    result = await db.execute(
        select(AgentConfig).where(AgentConfig.agent_name == AUTOPILOT_AGENT_NAME)
    )
    config = result.scalar_one_or_none()
    if config is not None:
        return config

    config = AgentConfig(
        agent_name=AUTOPILOT_AGENT_NAME,
        autonomy_level="semi",
        thresholds_json={
            "pressure_high": 70,
            "confidence_threshold": 0.7,
            "allow_autonomous_execute": False,
        },
        is_active=True,
    )
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


async def _current_staffing_pressure(db: AsyncSession, restaurant_id: int) -> float:
    active_orders_result = await db.execute(
        select(func.count(TableOrder.id)).where(
            TableOrder.restaurant_id == restaurant_id,
            TableOrder.status.in_(["open", "submitted", "preparing"]),
        )
    )
    preparing_items_result = await db.execute(
        select(func.count(OrderItem.id)).where(
            OrderItem.restaurant_id == restaurant_id,
            OrderItem.status.in_(["pending", "preparing"]),
        )
    )
    waiting_reservations_result = await db.execute(
        select(func.count(Reservation.id)).where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.status == "confirmed",
        )
    )

    active_orders = float(active_orders_result.scalar() or 0)
    preparing_items = float(preparing_items_result.scalar() or 0)
    waiting_reservations = float(waiting_reservations_result.scalar() or 0)

    raw = (active_orders * 7.5) + (preparing_items * 2.0) + (waiting_reservations * 5.5)
    return round(min(100.0, raw), 2)


async def _predict_wait_for_table(
    db: AsyncSession,
    restaurant_id: int,
    table: Table,
    horizon_minutes: int,
    staffing_pressure: float,
) -> tuple[float, float]:
    now = _now_utc()
    window_start = now - timedelta(minutes=120)

    orders_result = await db.execute(
        select(TableOrder).where(
            TableOrder.restaurant_id == restaurant_id,
            TableOrder.table_id == table.id,
            TableOrder.status.in_(["open", "submitted", "preparing", "served"]),
            TableOrder.created_at >= window_start,
        )
    )
    active_orders = list(orders_result.scalars().all())

    reservations_result = await db.execute(
        select(func.count(Reservation.id)).where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.table_id == table.id,
            Reservation.status.in_(["confirmed", "seated"]),
            Reservation.reservation_date == now.date(),
        )
    )
    reservation_count = float(reservations_result.scalar() or 0)

    elapsed_component = 0.0
    if active_orders:
        elapsed_values = []
        for order in active_orders:
            if order.created_at:
                elapsed_values.append(
                    max(0.0, (now - order.created_at).total_seconds() / 60.0)
                )
        if elapsed_values:
            elapsed_component = sum(elapsed_values) / len(elapsed_values)

    predicted_wait = (
        (len(active_orders) * 5.5)
        + (reservation_count * 3.5)
        + (elapsed_component * 0.25)
        + ((staffing_pressure / 100.0) * 10.0)
    )
    predicted_wait = max(0.0, min(90.0, predicted_wait))

    confidence = 0.92 - ((staffing_pressure / 100.0) * 0.18) - (len(active_orders) * 0.02)
    confidence = max(0.45, min(0.98, confidence))
    return round(predicted_wait, 2), round(confidence, 3)


async def _refresh_actuals_and_accuracy(
    db: AsyncSession, restaurant_id: int, horizon_minutes: int
) -> PredictorAccuracy:
    now = _now_utc()
    unresolved_result = await db.execute(
        select(ServiceAutopilotPrediction).where(
            ServiceAutopilotPrediction.restaurant_id == restaurant_id,
            ServiceAutopilotPrediction.horizon_minutes == horizon_minutes,
            ServiceAutopilotPrediction.target_time <= now,
            ServiceAutopilotPrediction.actual_wait_min.is_(None),
        )
    )
    unresolved = list(unresolved_result.scalars().all())

    for prediction in unresolved:
        if prediction.table_id is None:
            continue
        session_result = await db.execute(
            select(TableSession)
            .where(
                TableSession.restaurant_id == restaurant_id,
                TableSession.table_id == prediction.table_id,
                TableSession.started_at >= prediction.generated_at,
                TableSession.started_at <= prediction.target_time + timedelta(minutes=90),
            )
            .order_by(TableSession.started_at.asc())
            .limit(1)
        )
        session = session_result.scalar_one_or_none()
        if session is None:
            continue
        actual_wait = max(
            0.0, (session.started_at - prediction.target_time).total_seconds() / 60.0
        )
        prediction.actual_wait_min = round(actual_wait, 2)
        prediction.error_abs_min = round(
            abs(prediction.predicted_wait_min - prediction.actual_wait_min), 2
        )

    history_result = await db.execute(
        select(ServiceAutopilotPrediction).where(
            ServiceAutopilotPrediction.restaurant_id == restaurant_id,
            ServiceAutopilotPrediction.horizon_minutes == horizon_minutes,
            ServiceAutopilotPrediction.actual_wait_min.is_not(None),
            ServiceAutopilotPrediction.error_abs_min.is_not(None),
        )
    )
    history = list(history_result.scalars().all())
    if not history:
        return PredictorAccuracy(sample_size=0, last_updated_at=now)

    sample_size = len(history)
    mae = sum(float(row.error_abs_min or 0.0) for row in history) / sample_size
    within_10 = (
        sum(1 for row in history if float(row.error_abs_min or 0.0) <= 10.0) / sample_size
    ) * 100.0
    return PredictorAccuracy(
        sample_size=sample_size,
        mae_minutes=round(mae, 2),
        within_10_min_pct=round(within_10, 2),
        last_updated_at=now,
    )


async def predict_service_delay(
    db: AsyncSession,
    restaurant_id: int,
    horizon_minutes: int = 15,
) -> ServiceAutopilotPredictionResponse:
    _validate_horizon_minutes(horizon_minutes)
    now = _now_utc()
    target_time = now + timedelta(minutes=horizon_minutes)
    staffing_pressure = await _current_staffing_pressure(db, restaurant_id)

    tables_result = await db.execute(
        select(Table).where(Table.restaurant_id == restaurant_id, Table.is_active == True)
    )
    tables = list(tables_result.scalars().all())

    predictions: list[TableDelayPrediction] = []
    for table in tables:
        predicted_wait, confidence = await _predict_wait_for_table(
            db, restaurant_id, table, horizon_minutes, staffing_pressure
        )
        row = ServiceAutopilotPrediction(
            restaurant_id=restaurant_id,
            table_id=table.id,
            horizon_minutes=horizon_minutes,
            generated_at=now,
            target_time=target_time,
            predicted_wait_min=predicted_wait,
            staffing_pressure_score=staffing_pressure,
            confidence=confidence,
        )
        db.add(row)
        predictions.append(
            TableDelayPrediction(
                table_id=table.id,
                table_number=table.table_number,
                predicted_wait_min=predicted_wait,
                horizon_minutes=horizon_minutes,
                confidence=confidence,
                staffing_pressure_score=staffing_pressure,
                target_time=target_time,
            )
        )

    await db.flush()
    accuracy = await _refresh_actuals_and_accuracy(db, restaurant_id, horizon_minutes)
    return ServiceAutopilotPredictionResponse(
        generated_at=now,
        horizon_minutes=horizon_minutes,
        staffing_pressure_score=staffing_pressure,
        predictions=predictions,
        accuracy=accuracy,
    )


def _create_suggestion_action(
    *,
    title: str,
    action_type: str,
    rationale: str,
    projected_wait_delta_min: float,
    confidence: float,
    requires_approval: bool,
    payload: dict,
) -> ServiceAutopilotSuggestionRead:
    return ServiceAutopilotSuggestionRead(
        action_id=0,
        action_type=action_type,
        title=title,
        rationale=rationale,
        projected_wait_delta_min=round(projected_wait_delta_min, 2),
        confidence=round(confidence, 3),
        requires_approval=requires_approval,
        status="pending_approval" if requires_approval else "suggested",
        payload=payload,
    )


async def suggest_service_actions(
    db: AsyncSession,
    restaurant_id: int,
    horizon_minutes: int = 15,
) -> ServiceAutopilotSuggestResponse:
    _validate_horizon_minutes(horizon_minutes)
    prediction_snapshot = await predict_service_delay(db, restaurant_id, horizon_minutes)
    config = await _get_or_create_agent_config(db)
    thresholds = config.thresholds_json or {}
    confidence_threshold = float(thresholds.get("confidence_threshold", 0.7))
    pressure_high = float(thresholds.get("pressure_high", 70))

    sorted_predictions = sorted(
        prediction_snapshot.predictions, key=lambda item: item.predicted_wait_min, reverse=True
    )

    suggestions: list[ServiceAutopilotSuggestionRead] = []

    if sorted_predictions:
        highest = sorted_predictions[0]
        lowest = sorted_predictions[-1]
        if highest.table_id != lowest.table_id and highest.predicted_wait_min - lowest.predicted_wait_min >= 4:
            projected_delta = (highest.predicted_wait_min - lowest.predicted_wait_min) * 0.45
            suggestions.append(
                _create_suggestion_action(
                    title=f"Reassign table flow from T{highest.table_number} to T{lowest.table_number}",
                    action_type="reassign_table_flow",
                    rationale="Balancing queue load between high-delay and low-delay tables reduces local bottlenecks.",
                    projected_wait_delta_min=projected_delta,
                    confidence=min(highest.confidence, 0.9),
                    requires_approval=True,
                    payload={
                        "from_table_id": highest.table_id,
                        "to_table_id": lowest.table_id,
                        "horizon_minutes": horizon_minutes,
                    },
                )
            )

    if prediction_snapshot.staffing_pressure_score >= pressure_high:
        projected_delta = max(3.0, prediction_snapshot.staffing_pressure_score * 0.08)
        suggestions.append(
            _create_suggestion_action(
                title="Hold new seating for 10 minutes",
                action_type="hold_seating",
                rationale="Temporary hold allows kitchen and service stations to clear active ticket backlog.",
                projected_wait_delta_min=projected_delta,
                confidence=0.78,
                requires_approval=True,
                payload={"hold_minutes": 10, "horizon_minutes": horizon_minutes},
            )
        )

    order_result = await db.execute(
        select(TableOrder).where(
            TableOrder.restaurant_id == restaurant_id,
            TableOrder.status == "open",
        )
    )
    open_orders = list(order_result.scalars().all())
    if open_orders:
        projected_delta = min(8.0, 2.0 + (len(open_orders) * 0.5))
        suggestions.append(
            _create_suggestion_action(
                title="Push prep for open checks",
                action_type="push_prep",
                rationale="Prompting open checks to prep reduces idle time before kitchen acknowledgment.",
                projected_wait_delta_min=projected_delta,
                confidence=0.74,
                requires_approval=True,
                payload={"order_ids": [order.id for order in open_orders[:8]]},
            )
        )

    persisted: list[ServiceAutopilotSuggestionRead] = []
    for suggestion in suggestions:
        requires_approval = suggestion.requires_approval or suggestion.confidence < confidence_threshold
        agent_action = AgentAction(
            agent_name=AUTOPILOT_AGENT_NAME,
            action_type=suggestion.action_type,
            description=suggestion.title,
            input_data={"restaurant_id": restaurant_id, "payload": suggestion.payload},
            output_data={
                "rationale": suggestion.rationale,
                "projected_wait_delta_min": suggestion.projected_wait_delta_min,
                "entity_type": "reservations",
                "entity_id": suggestion.payload.get("from_table_id") or suggestion.payload.get("order_ids", [None])[0],
            },
            status="pending_approval" if requires_approval else "suggested",
            confidence=suggestion.confidence,
            requires_approval=requires_approval,
        )
        db.add(agent_action)
        await db.flush()

        suggestion.action_id = agent_action.id
        suggestion.requires_approval = requires_approval
        suggestion.status = agent_action.status
        persisted.append(suggestion)

    return ServiceAutopilotSuggestResponse(
        generated_at=_now_utc(),
        staffing_pressure_score=prediction_snapshot.staffing_pressure_score,
        suggestions=persisted,
    )


async def approve_service_action(
    db: AsyncSession,
    restaurant_id: int,
    action_id: int,
    user_id: int,
) -> ServiceAutopilotActionExecuteResponse:
    result = await db.execute(
        select(AgentAction).where(
            AgentAction.id == action_id,
            AgentAction.agent_name == AUTOPILOT_AGENT_NAME,
        )
    )
    action = result.scalar_one_or_none()
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    if _action_restaurant_id(action) != restaurant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")

    action.status = "approved"
    action.approved_by = user_id
    await db.flush()
    await log_human_action(
        db,
        action="service_autopilot_action_approved",
        detail=f"Approved Service Autopilot action #{action.id}",
        entity_type="reservations",
        entity_id=None,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=user_id,
    )
    emit_sensitive_audit(
        action="service_autopilot_action_approved",
        tenant_id=restaurant_id,
        user_id=user_id,
        agent_id=f"{AUTOPILOT_AGENT_NAME}:{action.id}",
        status="approved",
        detail=f"Approved action {action.id}",
        metadata={"action_type": action.action_type},
    )
    return ServiceAutopilotActionExecuteResponse(
        action_id=action.id,
        status=action.status,
        executed=False,
        message="Action approved. Execute explicitly to apply.",
    )


async def execute_service_action(
    db: AsyncSession,
    restaurant_id: int,
    action_id: int,
    user_id: int,
) -> ServiceAutopilotActionExecuteResponse:
    config = await _get_or_create_agent_config(db)
    thresholds = config.thresholds_json or {}
    allow_autonomous = bool(thresholds.get("allow_autonomous_execute", False))

    result = await db.execute(
        select(AgentAction).where(
            AgentAction.id == action_id,
            AgentAction.agent_name == AUTOPILOT_AGENT_NAME,
        )
    )
    action = result.scalar_one_or_none()
    if action is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    if _action_restaurant_id(action) != restaurant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")

    if action.requires_approval and action.status != "approved":
        emit_sensitive_audit(
            action="service_autopilot_action_execute_blocked",
            tenant_id=restaurant_id,
            user_id=user_id,
            agent_id=f"{AUTOPILOT_AGENT_NAME}:{action.id}",
            status="blocked",
            detail="Action requires approval before execution",
            metadata={"action_type": action.action_type},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Action requires approval before execution",
        )

    if not allow_autonomous and action.approved_by is None:
        emit_sensitive_audit(
            action="service_autopilot_action_execute_blocked",
            tenant_id=restaurant_id,
            user_id=user_id,
            agent_id=f"{AUTOPILOT_AGENT_NAME}:{action.id}",
            status="blocked",
            detail="Autonomous execution is disabled by policy",
            metadata={"action_type": action.action_type},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Autonomous execution is disabled by policy",
        )

    action.status = "executed"
    action.executed_at = _now_utc()
    if action.approved_by is None:
        action.approved_by = user_id
    await db.flush()

    await log_human_action(
        db,
        action="service_autopilot_action_executed",
        detail=f"Executed Service Autopilot action #{action.id} ({action.action_type})",
        entity_type="reservations",
        entity_id=None,
        source_module="agents",
        restaurant_id=restaurant_id,
        actor_user_id=user_id,
    )
    emit_sensitive_audit(
        action="service_autopilot_action_executed",
        tenant_id=restaurant_id,
        user_id=user_id,
        agent_id=f"{AUTOPILOT_AGENT_NAME}:{action.id}",
        status="executed",
        detail=f"Executed action {action.id}",
        metadata={"action_type": action.action_type},
    )
    return ServiceAutopilotActionExecuteResponse(
        action_id=action.id,
        status=action.status,
        executed=True,
        message="Action execution logged.",
    )
