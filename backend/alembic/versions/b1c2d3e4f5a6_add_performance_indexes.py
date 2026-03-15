"""add performance indexes

Revision ID: b1c2d3e4f5a6
Revises: 7a5db2f9da1f, d4e5f6g7h8i9
Create Date: 2026-03-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str]] = ("7a5db2f9da1f", "d4e5f6g7h8i9")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- auth: users ---
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_restaurant_id"), "users", ["restaurant_id"], unique=False)

    # --- billing: table_orders ---
    op.create_index(op.f("ix_table_orders_restaurant_id"), "table_orders", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_table_orders_status"), "table_orders", ["status"], unique=False)
    op.create_index("ix_table_orders_created_at", "table_orders", ["created_at"], unique=False)

    # --- billing: order_items ---
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"], unique=False)
    op.create_index(op.f("ix_order_items_status"), "order_items", ["status"], unique=False)

    # --- billing: bills ---
    op.create_index(op.f("ix_bills_order_id"), "bills", ["order_id"], unique=False)

    # --- billing: payments ---
    op.create_index(op.f("ix_payments_bill_id"), "payments", ["bill_id"], unique=False)

    # --- inventory: vendors ---
    op.create_index(op.f("ix_vendors_restaurant_id"), "vendors", ["restaurant_id"], unique=False)

    # --- inventory: inventory_items ---
    op.create_index(op.f("ix_inventory_items_restaurant_id"), "inventory_items", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_inventory_items_name"), "inventory_items", ["name"], unique=False)

    # --- inventory: purchase_orders ---
    op.create_index(op.f("ix_purchase_orders_restaurant_id"), "purchase_orders", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_purchase_orders_status"), "purchase_orders", ["status"], unique=False)

    # --- reservations: tables ---
    op.create_index(op.f("ix_tables_restaurant_id"), "tables", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_tables_section_id"), "tables", ["section_id"], unique=False)

    # --- reservations: reservations ---
    op.create_index(op.f("ix_reservations_restaurant_id"), "reservations", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_reservations_reservation_date"), "reservations", ["reservation_date"], unique=False)
    op.create_index(op.f("ix_reservations_status"), "reservations", ["status"], unique=False)

    # --- reservations: table_sessions ---
    op.create_index(op.f("ix_table_sessions_table_id"), "table_sessions", ["table_id"], unique=False)

    # --- guests: guest_profiles ---
    op.create_index(op.f("ix_guest_profiles_restaurant_id"), "guest_profiles", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_guest_profiles_email"), "guest_profiles", ["email"], unique=False)

    # --- guests: orders ---
    op.create_index(op.f("ix_orders_guest_id"), "orders", ["guest_id"], unique=False)

    # --- menu: menu_categories ---
    op.create_index(op.f("ix_menu_categories_restaurant_id"), "menu_categories", ["restaurant_id"], unique=False)

    # --- menu: menu_items ---
    op.create_index(op.f("ix_menu_items_restaurant_id"), "menu_items", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_menu_items_category_id"), "menu_items", ["category_id"], unique=False)


def downgrade() -> None:
    # --- menu ---
    op.drop_index(op.f("ix_menu_items_category_id"), table_name="menu_items")
    op.drop_index(op.f("ix_menu_items_restaurant_id"), table_name="menu_items")
    op.drop_index(op.f("ix_menu_categories_restaurant_id"), table_name="menu_categories")

    # --- guests ---
    op.drop_index(op.f("ix_orders_guest_id"), table_name="orders")
    op.drop_index(op.f("ix_guest_profiles_email"), table_name="guest_profiles")
    op.drop_index(op.f("ix_guest_profiles_restaurant_id"), table_name="guest_profiles")

    # --- reservations ---
    op.drop_index(op.f("ix_table_sessions_table_id"), table_name="table_sessions")
    op.drop_index(op.f("ix_reservations_status"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_reservation_date"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_restaurant_id"), table_name="reservations")
    op.drop_index(op.f("ix_tables_section_id"), table_name="tables")
    op.drop_index(op.f("ix_tables_restaurant_id"), table_name="tables")

    # --- inventory ---
    op.drop_index(op.f("ix_purchase_orders_status"), table_name="purchase_orders")
    op.drop_index(op.f("ix_purchase_orders_restaurant_id"), table_name="purchase_orders")
    op.drop_index(op.f("ix_inventory_items_name"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_restaurant_id"), table_name="inventory_items")
    op.drop_index(op.f("ix_vendors_restaurant_id"), table_name="vendors")

    # --- billing ---
    op.drop_index(op.f("ix_payments_bill_id"), table_name="payments")
    op.drop_index(op.f("ix_bills_order_id"), table_name="bills")
    op.drop_index(op.f("ix_order_items_status"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_index("ix_table_orders_created_at", table_name="table_orders")
    op.drop_index(op.f("ix_table_orders_status"), table_name="table_orders")
    op.drop_index(op.f("ix_table_orders_restaurant_id"), table_name="table_orders")

    # --- auth ---
    op.drop_index(op.f("ix_users_restaurant_id"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
