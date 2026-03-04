from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole

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


async def test_service_autopilot_predict_and_suggest_contract(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    predict = await client.get(
        "/api/agents/service-autopilot/predict?horizon_minutes=15",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert predict.status_code == 200
    predict_data = predict.json()
    assert predict_data["horizon_minutes"] == 15
    assert "staffing_pressure_score" in predict_data
    assert isinstance(predict_data["predictions"], list)
    assert len(predict_data["predictions"]) >= 1
    assert "accuracy" in predict_data
    assert "sample_size" in predict_data["accuracy"]

    suggest = await client.post(
        "/api/agents/service-autopilot/suggest?horizon_minutes=15",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert suggest.status_code == 200
    suggest_data = suggest.json()
    assert isinstance(suggest_data["suggestions"], list)
    assert len(suggest_data["suggestions"]) >= 1
    first = suggest_data["suggestions"][0]
    assert "projected_wait_delta_min" in first
    assert first["projected_wait_delta_min"] >= 0


async def test_service_autopilot_requires_human_approval_by_default(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    suggest = await client.post(
        "/api/agents/service-autopilot/suggest?horizon_minutes=15",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert suggest.status_code == 200
    suggestion = suggest.json()["suggestions"][0]
    action_id = suggestion["action_id"]

    execute_without_approval = await client.post(
        f"/api/agents/service-autopilot/actions/{action_id}/execute",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert execute_without_approval.status_code == 409
    assert "requires approval" in execute_without_approval.json()["detail"]

    approve = await client.post(
        f"/api/agents/service-autopilot/actions/{action_id}/approve",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    execute_after_approval = await client.post(
        f"/api/agents/service-autopilot/actions/{action_id}/execute",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert execute_after_approval.status_code == 200
    body = execute_after_approval.json()
    assert body["executed"] is True
    assert body["status"] == "executed"


async def test_service_autopilot_cross_tenant_action_access_isolated(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    suggest = await client.post(
        "/api/agents/service-autopilot/suggest?horizon_minutes=15",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert suggest.status_code == 200
    action_id = suggest.json()["suggestions"][0]["action_id"]

    cross_approve = await client.post(
        f"/api/agents/service-autopilot/actions/{action_id}/approve",
        headers=tenant_headers(tenant_seed.restaurant_b_id),
    )
    assert cross_approve.status_code == 404

    cross_execute = await client.post(
        f"/api/agents/service-autopilot/actions/{action_id}/execute",
        headers=tenant_headers(tenant_seed.restaurant_b_id),
    )
    assert cross_execute.status_code == 404


async def test_service_autopilot_horizon_validation(
    client: AsyncClient, tenant_seed: Any, db_session: AsyncSession
) -> None:
    await ensure_actor_user(db_session, tenant_seed.restaurant_a_id)

    invalid_predict = await client.get(
        "/api/agents/service-autopilot/predict?horizon_minutes=17",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert invalid_predict.status_code == 422
