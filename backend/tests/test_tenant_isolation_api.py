from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


def tenant_headers(restaurant_id: int, role: str = "manager") -> dict[str, str]:
    return {
        "x-test-restaurant-id": str(restaurant_id),
        "x-test-role": role,
    }


async def test_menu_cross_tenant_access_isolation(client: AsyncClient, tenant_seed: Any) -> None:
    own = await client.get(
        f"/api/menu/items/{tenant_seed.menu_item_a_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert own.status_code == 200
    assert own.json()["id"] == tenant_seed.menu_item_a_id

    cross_read = await client.get(
        f"/api/menu/items/{tenant_seed.menu_item_b_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_read.status_code == 404

    cross_update = await client.put(
        f"/api/menu/items/{tenant_seed.menu_item_b_id}",
        json={"name": "Cross Tenant Attempt"},
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_update.status_code == 404


async def test_guests_cross_tenant_access_isolation(client: AsyncClient, tenant_seed: Any) -> None:
    own = await client.get(
        f"/api/guests/{tenant_seed.guest_a_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert own.status_code == 200
    assert own.json()["id"] == tenant_seed.guest_a_id

    cross_read = await client.get(
        f"/api/guests/{tenant_seed.guest_b_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_read.status_code == 404

    cross_write = await client.post(
        "/api/guests/orders",
        json={
            "guest_id": tenant_seed.guest_b_id,
            "order_date": datetime.now(timezone.utc).isoformat(),
            "channel": "dine_in",
            "total": 24.5,
            "items_json": {"items": [{"name": "Soup", "qty": 1}]},
            "discount": 0,
            "tip": 0,
        },
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_write.status_code == 404


async def test_reservations_cross_tenant_access_isolation(
    client: AsyncClient, tenant_seed: Any
) -> None:
    own = await client.get(
        f"/api/reservations/{tenant_seed.reservation_a_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert own.status_code == 200
    assert own.json()["id"] == tenant_seed.reservation_a_id

    cross_read = await client.get(
        f"/api/reservations/{tenant_seed.reservation_b_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_read.status_code == 404

    cross_write = await client.post(
        "/api/reservations/sessions",
        json={
            "table_id": tenant_seed.table_b_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "covers": 2,
        },
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_write.status_code == 404


async def test_billing_cross_tenant_access_isolation(
    client: AsyncClient, tenant_seed: Any
) -> None:
    own = await client.get(
        f"/api/billing/orders/{tenant_seed.billing_order_a_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert own.status_code == 200
    assert own.json()["id"] == tenant_seed.billing_order_a_id

    cross_read = await client.get(
        f"/api/billing/orders/{tenant_seed.billing_order_b_id}",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_read.status_code == 404

    cross_write = await client.post(
        f"/api/billing/orders/{tenant_seed.billing_order_b_id}/items",
        json={
            "menu_item_id": tenant_seed.menu_item_a_id,
            "item_name": "Cross Item",
            "quantity": 1,
            "unit_price": 10.0,
            "modifiers_json": {"extra": []},
        },
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_write.status_code == 404


async def test_inventory_cross_tenant_access_isolation(
    client: AsyncClient, tenant_seed: Any
) -> None:
    own_list = await client.get(
        "/api/inventory/items",
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert own_list.status_code == 200
    own_ids = {item["id"] for item in own_list.json()}
    assert tenant_seed.inventory_item_a_id in own_ids
    assert tenant_seed.inventory_item_b_id not in own_ids

    cross_update = await client.put(
        f"/api/inventory/items/{tenant_seed.inventory_item_b_id}",
        json={"par_level": 999},
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_update.status_code == 404

    cross_order_create = await client.post(
        "/api/inventory/orders",
        json={
            "vendor_id": tenant_seed.vendor_b_id,
            "order_date": date.today().isoformat(),
            "total": 200,
            "line_items_json": {"items": []},
        },
        headers=tenant_headers(tenant_seed.restaurant_a_id),
    )
    assert cross_order_create.status_code == 404
