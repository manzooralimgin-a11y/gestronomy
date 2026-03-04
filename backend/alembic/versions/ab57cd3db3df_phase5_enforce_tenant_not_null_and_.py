"""phase5 enforce tenant not null and scoped uniques

Revision ID: ab57cd3db3df
Revises: 9b4c1d2e7f10
Create Date: 2026-03-03 22:04:40.380796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab57cd3db3df'
down_revision: Union[str, None] = '9b4c1d2e7f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TENANT_TABLES = [
    "menu_categories",
    "menu_items",
    "menu_modifiers",
    "menu_combos",
    "upsell_rules",
    "guest_profiles",
    "orders",
    "loyalty_accounts",
    "promotions",
    "floor_sections",
    "tables",
    "reservations",
    "waitlist",
    "qr_table_codes",
    "table_sessions",
    "table_orders",
    "order_items",
    "bills",
    "payments",
    "cash_shifts",
    "kds_station_configs",
    "vendors",
    "inventory_items",
    "purchase_orders",
    "inventory_movements",
    "tva_reports",
    "supplier_catalog_items",
    "auto_purchase_rules",
]

LEGACY_TENANT_NAME = "__legacy_unassigned_tenant__"


def _execute_statements(bind, statements: list[str], params: dict | None = None) -> None:
    for statement in statements:
        bind.execute(sa.text(statement), params or {})


def _get_or_create_legacy_restaurant_id(bind) -> int:
    row = bind.execute(
        sa.text("SELECT id FROM restaurants WHERE name = :name ORDER BY id LIMIT 1"),
        {"name": LEGACY_TENANT_NAME},
    ).fetchone()
    if row is not None:
        return int(row[0])

    return int(
        bind.execute(
            sa.text(
                """
                INSERT INTO restaurants (
                    name, address, city, state, zip_code, phone, timezone, currency, settings_json
                )
                VALUES (
                    :name, 'Legacy Data (Unassigned)', 'N/A', 'N/A', '00000', '0000000000',
                    'America/New_York', 'USD', '{}'::json
                )
                RETURNING id
                """
            ),
            {"name": LEGACY_TENANT_NAME},
        ).scalar_one()
    )


def upgrade() -> None:
    bind = op.get_bind()

    # Second-pass deterministic backfill from related tables.
    _execute_statements(
        bind,
        [
            """
            UPDATE menu_categories mc
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT category_id, MIN(restaurant_id) AS restaurant_id
                FROM menu_items
                WHERE restaurant_id IS NOT NULL
                GROUP BY category_id
            ) src
            WHERE mc.id = src.category_id
              AND mc.restaurant_id IS NULL
            """,
            """
            UPDATE menu_items mi
            SET restaurant_id = mc.restaurant_id
            FROM menu_categories mc
            WHERE mi.category_id = mc.id
              AND mi.restaurant_id IS NULL
            """,
            """
            UPDATE menu_modifiers mm
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT mim.modifier_id, MIN(mi.restaurant_id) AS restaurant_id
                FROM menu_item_modifiers mim
                JOIN menu_items mi ON mi.id = mim.item_id
                WHERE mi.restaurant_id IS NOT NULL
                GROUP BY mim.modifier_id
            ) src
            WHERE mm.id = src.modifier_id
              AND mm.restaurant_id IS NULL
            """,
            """
            UPDATE menu_combos mc
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT MIN(mi.restaurant_id) AS restaurant_id
                FROM menu_items mi
                WHERE mi.restaurant_id IS NOT NULL
            ) src
            WHERE mc.restaurant_id IS NULL
            """,
            """
            UPDATE guest_profiles gp
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT guest_id, MIN(restaurant_id) AS restaurant_id
                FROM orders
                WHERE guest_id IS NOT NULL AND restaurant_id IS NOT NULL
                GROUP BY guest_id
            ) src
            WHERE gp.id = src.guest_id
              AND gp.restaurant_id IS NULL
            """,
            """
            UPDATE floor_sections fs
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT section_id, MIN(restaurant_id) AS restaurant_id
                FROM tables
                WHERE restaurant_id IS NOT NULL
                GROUP BY section_id
            ) src
            WHERE fs.id = src.section_id
              AND fs.restaurant_id IS NULL
            """,
            """
            UPDATE tables t
            SET restaurant_id = fs.restaurant_id
            FROM floor_sections fs
            WHERE t.section_id = fs.id
              AND t.restaurant_id IS NULL
            """,
            """
            UPDATE reservations r
            SET restaurant_id = t.restaurant_id
            FROM tables t
            WHERE r.table_id = t.id
              AND r.restaurant_id IS NULL
            """,
            """
            UPDATE reservations r
            SET restaurant_id = gp.restaurant_id
            FROM guest_profiles gp
            WHERE r.guest_id = gp.id
              AND r.restaurant_id IS NULL
            """,
            """
            UPDATE reservations r
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT reservation_id, MIN(restaurant_id) AS restaurant_id
                FROM table_sessions
                WHERE reservation_id IS NOT NULL AND restaurant_id IS NOT NULL
                GROUP BY reservation_id
            ) src
            WHERE r.id = src.reservation_id
              AND r.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_items ii
            SET restaurant_id = v.restaurant_id
            FROM vendors v
            WHERE ii.vendor_id = v.id
              AND ii.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_items ii
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT item_id, MIN(restaurant_id) AS restaurant_id
                FROM inventory_movements
                WHERE restaurant_id IS NOT NULL
                GROUP BY item_id
            ) src
            WHERE ii.id = src.item_id
              AND ii.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_items ii
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT item_id, MIN(restaurant_id) AS restaurant_id
                FROM tva_reports
                WHERE restaurant_id IS NOT NULL
                GROUP BY item_id
            ) src
            WHERE ii.id = src.item_id
              AND ii.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_items ii
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT inventory_item_id, MIN(restaurant_id) AS restaurant_id
                FROM supplier_catalog_items
                WHERE inventory_item_id IS NOT NULL AND restaurant_id IS NOT NULL
                GROUP BY inventory_item_id
            ) src
            WHERE ii.id = src.inventory_item_id
              AND ii.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_items ii
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT inventory_item_id, MIN(restaurant_id) AS restaurant_id
                FROM auto_purchase_rules
                WHERE restaurant_id IS NOT NULL
                GROUP BY inventory_item_id
            ) src
            WHERE ii.id = src.inventory_item_id
              AND ii.restaurant_id IS NULL
            """,
            """
            UPDATE vendors v
            SET restaurant_id = src.restaurant_id
            FROM (
                SELECT vendor_id, MIN(restaurant_id) AS restaurant_id
                FROM purchase_orders
                WHERE vendor_id IS NOT NULL AND restaurant_id IS NOT NULL
                GROUP BY vendor_id
            ) src
            WHERE v.id = src.vendor_id
              AND v.restaurant_id IS NULL
            """,
        ],
    )

    # Fallback for orphaned legacy rows so NOT NULL can be enforced safely.
    legacy_restaurant_id = _get_or_create_legacy_restaurant_id(bind)
    for table_name in TENANT_TABLES:
        bind.execute(
            sa.text(f"UPDATE {table_name} SET restaurant_id = :rid WHERE restaurant_id IS NULL"),
            {"rid": legacy_restaurant_id},
        )

    # Convert global unique constraints to tenant-scoped uniques.
    op.drop_constraint("bills_bill_number_key", "bills", type_="unique")
    op.create_unique_constraint(
        "uq_bills_restaurant_id_bill_number",
        "bills",
        ["restaurant_id", "bill_number"],
    )

    op.drop_constraint("kds_station_configs_name_key", "kds_station_configs", type_="unique")
    op.create_unique_constraint(
        "uq_kds_station_configs_restaurant_id_name",
        "kds_station_configs",
        ["restaurant_id", "name"],
    )

    for table_name in TENANT_TABLES:
        op.alter_column(
            table_name,
            "restaurant_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    for table_name in reversed(TENANT_TABLES):
        op.alter_column(
            table_name,
            "restaurant_id",
            existing_type=sa.Integer(),
            nullable=True,
        )

    op.drop_constraint(
        "uq_bills_restaurant_id_bill_number",
        "bills",
        type_="unique",
    )
    op.create_unique_constraint(
        "bills_bill_number_key",
        "bills",
        ["bill_number"],
    )

    op.drop_constraint(
        "uq_kds_station_configs_restaurant_id_name",
        "kds_station_configs",
        type_="unique",
    )
    op.create_unique_constraint(
        "kds_station_configs_name_key",
        "kds_station_configs",
        ["name"],
    )
