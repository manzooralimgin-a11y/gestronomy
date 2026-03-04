from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import date, datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import Restaurant, UserRole
from app.billing.models import TableOrder
from app.database import engine
from app.dependencies import get_current_tenant_user
from app.guests.models import GuestProfile
from app.inventory.models import InventoryItem, Vendor
from app.main import app
from app.menu.models import MenuCategory, MenuItem
from app.reservations.models import FloorSection, Reservation, Table


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            pass

    async def override_get_current_tenant(request: Request):
        tenant_header = request.headers.get("x-test-restaurant-id")
        role_header = (request.headers.get("x-test-role") or UserRole.manager.value).lower()
        restaurant_id = int(tenant_header) if tenant_header else 0
        role = UserRole(role_header)
        return SimpleNamespace(
            id=999_999,
            email="tenant-test@example.com",
            is_active=True,
            restaurant_id=restaurant_id,
            role=role,
        )

    from app.database import get_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_tenant_user] = override_get_current_tenant

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@dataclass
class TenantSeed:
    restaurant_a_id: int
    restaurant_b_id: int
    menu_item_a_id: int
    menu_item_b_id: int
    guest_a_id: int
    guest_b_id: int
    table_a_id: int
    table_b_id: int
    reservation_a_id: int
    reservation_b_id: int
    billing_order_a_id: int
    billing_order_b_id: int
    inventory_item_a_id: int
    inventory_item_b_id: int
    vendor_a_id: int
    vendor_b_id: int


@pytest_asyncio.fixture
async def tenant_seed(db_session: AsyncSession) -> TenantSeed:
    suffix = uuid4().hex[:8]

    restaurant_a = Restaurant(
        name=f"Tenant A {suffix}",
        address="100 A Street",
        city="A City",
        state="CA",
        zip_code="90001",
        phone=f"555100{suffix[:4]}",
    )
    restaurant_b = Restaurant(
        name=f"Tenant B {suffix}",
        address="200 B Street",
        city="B City",
        state="CA",
        zip_code="90002",
        phone=f"555200{suffix[:4]}",
    )
    db_session.add_all([restaurant_a, restaurant_b])
    await db_session.flush()

    cat_a = MenuCategory(name=f"Cat A {suffix}", restaurant_id=restaurant_a.id)
    cat_b = MenuCategory(name=f"Cat B {suffix}", restaurant_id=restaurant_b.id)
    db_session.add_all([cat_a, cat_b])
    await db_session.flush()

    menu_item_a = MenuItem(
        restaurant_id=restaurant_a.id,
        category_id=cat_a.id,
        name=f"Menu A {suffix}",
        price=12.50,
        cost=5.00,
    )
    menu_item_b = MenuItem(
        restaurant_id=restaurant_b.id,
        category_id=cat_b.id,
        name=f"Menu B {suffix}",
        price=18.00,
        cost=7.00,
    )
    db_session.add_all([menu_item_a, menu_item_b])

    guest_a = GuestProfile(
        restaurant_id=restaurant_a.id,
        name=f"Guest A {suffix}",
        email=f"guest-a-{suffix}@example.com",
    )
    guest_b = GuestProfile(
        restaurant_id=restaurant_b.id,
        name=f"Guest B {suffix}",
        email=f"guest-b-{suffix}@example.com",
    )
    db_session.add_all([guest_a, guest_b])

    section_a = FloorSection(name=f"Section A {suffix}", restaurant_id=restaurant_a.id)
    section_b = FloorSection(name=f"Section B {suffix}", restaurant_id=restaurant_b.id)
    db_session.add_all([section_a, section_b])
    await db_session.flush()

    table_a = Table(
        restaurant_id=restaurant_a.id,
        section_id=section_a.id,
        table_number=f"A-{suffix[:4]}",
        capacity=4,
    )
    table_b = Table(
        restaurant_id=restaurant_b.id,
        section_id=section_b.id,
        table_number=f"B-{suffix[:4]}",
        capacity=4,
    )
    db_session.add_all([table_a, table_b])
    await db_session.flush()

    reservation_a = Reservation(
        restaurant_id=restaurant_a.id,
        guest_id=guest_a.id,
        guest_name=guest_a.name or "Guest A",
        table_id=table_a.id,
        party_size=2,
        reservation_date=date.today(),
        start_time=datetime.now(timezone.utc).time().replace(microsecond=0),
    )
    reservation_b = Reservation(
        restaurant_id=restaurant_b.id,
        guest_id=guest_b.id,
        guest_name=guest_b.name or "Guest B",
        table_id=table_b.id,
        party_size=2,
        reservation_date=date.today(),
        start_time=datetime.now(timezone.utc).time().replace(microsecond=0),
    )
    db_session.add_all([reservation_a, reservation_b])

    order_a = TableOrder(restaurant_id=restaurant_a.id, table_id=table_a.id, guest_name="Billing A")
    order_b = TableOrder(restaurant_id=restaurant_b.id, table_id=table_b.id, guest_name="Billing B")
    db_session.add_all([order_a, order_b])

    vendor_a = Vendor(restaurant_id=restaurant_a.id, name=f"Vendor A {suffix}")
    vendor_b = Vendor(restaurant_id=restaurant_b.id, name=f"Vendor B {suffix}")
    db_session.add_all([vendor_a, vendor_b])
    await db_session.flush()

    inv_a = InventoryItem(
        restaurant_id=restaurant_a.id,
        name=f"Inventory A {suffix}",
        category="Produce",
        unit="kg",
        vendor_id=vendor_a.id,
    )
    inv_b = InventoryItem(
        restaurant_id=restaurant_b.id,
        name=f"Inventory B {suffix}",
        category="Produce",
        unit="kg",
        vendor_id=vendor_b.id,
    )
    db_session.add_all([inv_a, inv_b])
    await db_session.flush()

    return TenantSeed(
        restaurant_a_id=restaurant_a.id,
        restaurant_b_id=restaurant_b.id,
        menu_item_a_id=menu_item_a.id,
        menu_item_b_id=menu_item_b.id,
        guest_a_id=guest_a.id,
        guest_b_id=guest_b.id,
        table_a_id=table_a.id,
        table_b_id=table_b.id,
        reservation_a_id=reservation_a.id,
        reservation_b_id=reservation_b.id,
        billing_order_a_id=order_a.id,
        billing_order_b_id=order_b.id,
        inventory_item_a_id=inv_a.id,
        inventory_item_b_id=inv_b.id,
        vendor_a_id=vendor_a.id,
        vendor_b_id=vendor_b.id,
    )
