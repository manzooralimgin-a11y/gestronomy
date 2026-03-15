"""Auth module API tests — validation-only (no DB queries)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_missing_credentials(client: AsyncClient) -> None:
    resp = await client.post("/api/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient) -> None:
    resp = await client.post("/api/auth/register", json={})
    assert resp.status_code == 422
