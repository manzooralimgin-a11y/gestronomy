"""phase4 add restaurant_id to core tables

Revision ID: 9b4c1d2e7f10
Revises: 83ccdefe48ab
Create Date: 2026-03-03 05:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b4c1d2e7f10"
down_revision: Union[str, None] = "83ccdefe48ab"
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


def _execute_statements(bind, statements: list[str], params: dict | None = None) -> None:
    for statement in statements:
        bind.execute(sa.text(statement), params or {})


def _add_tenant_column(table_name: str) -> None:
    op.add_column(table_name, sa.Column("restaurant_id", sa.Integer(), nullable=True))
    op.create_index(f"ix_{table_name}_restaurant_id", table_name, ["restaurant_id"], unique=False)
    op.create_foreign_key(
        f"fk_{table_name}_restaurant_id_restaurants",
        table_name,
        "restaurants",
        ["restaurant_id"],
        ["id"],
        ondelete="SET NULL",
    )


def _drop_tenant_column(table_name: str) -> None:
    op.drop_constraint(f"fk_{table_name}_restaurant_id_restaurants", table_name, type_="foreignkey")
    op.drop_index(f"ix_{table_name}_restaurant_id", table_name=table_name)
    op.drop_column(table_name, "restaurant_id")


def upgrade() -> None:
    for table_name in TENANT_TABLES:
        _add_tenant_column(table_name)

    bind = op.get_bind()

    restaurants = list(bind.execute(sa.text("SELECT id FROM restaurants ORDER BY id LIMIT 2")))
    single_restaurant_id = restaurants[0][0] if len(restaurants) == 1 else None

    if single_restaurant_id is not None:
        _execute_statements(
            bind,
            [
                "UPDATE menu_categories SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE menu_modifiers SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE menu_combos SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE guest_profiles SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE floor_sections SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE waitlist SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE cash_shifts SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE kds_station_configs SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE vendors SET restaurant_id = :rid WHERE restaurant_id IS NULL",
                "UPDATE inventory_items SET restaurant_id = :rid WHERE restaurant_id IS NULL",
            ],
            {"rid": single_restaurant_id},
        )

    _execute_statements(
        bind,
        [
            """
            UPDATE menu_items mi
            SET restaurant_id = mc.restaurant_id
            FROM menu_categories mc
            WHERE mi.category_id = mc.id
              AND mi.restaurant_id IS NULL
            """,
            """
            UPDATE upsell_rules ur
            SET restaurant_id = mi.restaurant_id
            FROM menu_items mi
            WHERE ur.trigger_item_id = mi.id
              AND ur.restaurant_id IS NULL
            """,
            """
            UPDATE orders o
            SET restaurant_id = gp.restaurant_id
            FROM guest_profiles gp
            WHERE o.guest_id = gp.id
              AND o.restaurant_id IS NULL
            """,
            """
            UPDATE loyalty_accounts la
            SET restaurant_id = gp.restaurant_id
            FROM guest_profiles gp
            WHERE la.guest_id = gp.id
              AND la.restaurant_id IS NULL
            """,
            """
            UPDATE promotions p
            SET restaurant_id = gp.restaurant_id
            FROM guest_profiles gp
            WHERE p.guest_id = gp.id
              AND p.restaurant_id IS NULL
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
            UPDATE qr_table_codes q
            SET restaurant_id = t.restaurant_id
            FROM tables t
            WHERE q.table_id = t.id
              AND q.restaurant_id IS NULL
            """,
            """
            UPDATE table_sessions ts
            SET restaurant_id = t.restaurant_id
            FROM tables t
            WHERE ts.table_id = t.id
              AND ts.restaurant_id IS NULL
            """,
            """
            UPDATE table_sessions ts
            SET restaurant_id = r.restaurant_id
            FROM reservations r
            WHERE ts.reservation_id = r.id
              AND ts.restaurant_id IS NULL
            """,
            """
            UPDATE table_orders o
            SET restaurant_id = t.restaurant_id
            FROM tables t
            WHERE o.table_id = t.id
              AND o.restaurant_id IS NULL
            """,
            """
            UPDATE table_orders o
            SET restaurant_id = ts.restaurant_id
            FROM table_sessions ts
            WHERE o.session_id = ts.id
              AND o.restaurant_id IS NULL
            """,
            """
            UPDATE order_items oi
            SET restaurant_id = o.restaurant_id
            FROM table_orders o
            WHERE oi.order_id = o.id
              AND oi.restaurant_id IS NULL
            """,
            """
            UPDATE bills b
            SET restaurant_id = o.restaurant_id
            FROM table_orders o
            WHERE b.order_id = o.id
              AND b.restaurant_id IS NULL
            """,
            """
            UPDATE payments p
            SET restaurant_id = b.restaurant_id
            FROM bills b
            WHERE p.bill_id = b.id
              AND p.restaurant_id IS NULL
            """,
            """
            UPDATE purchase_orders po
            SET restaurant_id = v.restaurant_id
            FROM vendors v
            WHERE po.vendor_id = v.id
              AND po.restaurant_id IS NULL
            """,
            """
            UPDATE inventory_movements im
            SET restaurant_id = ii.restaurant_id
            FROM inventory_items ii
            WHERE im.item_id = ii.id
              AND im.restaurant_id IS NULL
            """,
            """
            UPDATE tva_reports tr
            SET restaurant_id = ii.restaurant_id
            FROM inventory_items ii
            WHERE tr.item_id = ii.id
              AND tr.restaurant_id IS NULL
            """,
            """
            UPDATE supplier_catalog_items sci
            SET restaurant_id = v.restaurant_id
            FROM vendors v
            WHERE sci.vendor_id = v.id
              AND sci.restaurant_id IS NULL
            """,
            """
            UPDATE supplier_catalog_items sci
            SET restaurant_id = ii.restaurant_id
            FROM inventory_items ii
            WHERE sci.inventory_item_id = ii.id
              AND sci.restaurant_id IS NULL
            """,
            """
            UPDATE auto_purchase_rules apr
            SET restaurant_id = ii.restaurant_id
            FROM inventory_items ii
            WHERE apr.inventory_item_id = ii.id
              AND apr.restaurant_id IS NULL
            """,
        ],
    )


def downgrade() -> None:
    for table_name in reversed(TENANT_TABLES):
        _drop_tenant_column(table_name)
