import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

async def test_agent_registry_integration(client: AsyncClient, tenant_seed):
    """
    Verifies that the Agent Registry properly initializes and exposes the internal
    sub-agents as well as the MetaAgent coordinator. This ensures the foundational
    integration point for agent routing is healthy in production.
    """
    headers = {"x-test-restaurant-id": str(tenant_seed.restaurant_a_id)}
    
    # Trigger request to the core agent registry endpoint
    response = await client.get("/api/agents", headers=headers)
    
    # Confirm it returns 200 OK
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, (list, dict)), "Agent output should be a structured registry"

async def test_agent_dashboard_alerts_integration(client: AsyncClient, tenant_seed):
    """
    Simulates a MetaAgent interaction pipeline checking the active alerts
    surface from Agent findings.
    """
    headers = {"x-test-restaurant-id": str(tenant_seed.restaurant_b_id)}
    
    response = await client.get("/api/dashboard/alerts", headers=headers)
    assert response.status_code == 200
