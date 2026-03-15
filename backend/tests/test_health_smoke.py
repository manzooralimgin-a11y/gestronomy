"""Smoke tests — verify critical endpoints respond correctly."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient) -> None:
    resp = await client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_requests_all_time" in data
    assert "top_endpoints" in data


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/api/nonexistent")
    assert resp.status_code in (404, 405)


@pytest.mark.asyncio
async def test_restore_all_removed(client: AsyncClient) -> None:
    """Verify the unauthenticated /restore-all endpoint no longer exists."""
    resp = await client.get("/restore-all")
    assert resp.status_code in (404, 405)
