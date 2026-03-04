from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


def tenant_headers(restaurant_id: int, role: str = "manager") -> dict[str, str]:
    return {
        "x-test-restaurant-id": str(restaurant_id),
        "x-test-role": role,
    }


async def test_slo_dashboard_shape(client: AsyncClient, tenant_seed) -> None:
    response = await client.get(
        "/api/dashboard/slo?window_minutes=15",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert response.status_code == 200
    body = response.json()
    assert "api_p95_latency_ms" in body
    assert "api_error_rate_pct" in body
    assert "queue_lag" in body
    assert "thresholds" in body
    assert "breaches" in body
