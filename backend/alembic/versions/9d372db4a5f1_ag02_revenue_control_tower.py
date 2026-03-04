"""ag02 revenue control tower

Revision ID: 9d372db4a5f1
Revises: 620206e756c2
Create Date: 2026-03-04 03:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d372db4a5f1"
down_revision: Union[str, None] = "620206e756c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "revenue_control_policies",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("kill_switch", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("daily_budget_cap", sa.Numeric(12, 2), nullable=False, server_default="500"),
        sa.Column("experiment_budget_cap", sa.Numeric(12, 2), nullable=False, server_default="200"),
        sa.Column("max_discount_pct", sa.Float(), nullable=False, server_default="30"),
        sa.Column("max_price_change_pct", sa.Float(), nullable=False, server_default="25"),
        sa.Column("min_margin_pct", sa.Float(), nullable=False, server_default="15"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", name="uq_revenue_control_policies_restaurant_id"),
    )
    op.create_index(
        "ix_revenue_control_policies_restaurant_id",
        "revenue_control_policies",
        ["restaurant_id"],
        unique=False,
    )

    op.create_table(
        "revenue_experiments",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("experiment_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("budget_cap", sa.Numeric(12, 2), nullable=True),
        sa.Column("exposures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("spent_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_revenue_experiments_restaurant_status",
        "revenue_experiments",
        ["restaurant_id", "status"],
        unique=False,
    )

    op.create_table(
        "revenue_experiment_events",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("variant_key", sa.String(length=80), nullable=False),
        sa.Column("exposures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("spend_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["experiment_id"], ["revenue_experiments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_revenue_experiment_events_restaurant_recorded",
        "revenue_experiment_events",
        ["restaurant_id", "recorded_at"],
        unique=False,
    )
    op.create_index(
        "ix_revenue_experiment_events_experiment_variant",
        "revenue_experiment_events",
        ["experiment_id", "variant_key"],
        unique=False,
    )

    op.create_table(
        "revenue_upsell_recommendations",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("guest_id", sa.Integer(), nullable=True),
        sa.Column("menu_item_id", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expected_uplift", sa.Numeric(12, 2), nullable=False),
        sa.Column("factors_json", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["guest_id"], ["guest_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["menu_item_id"], ["menu_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_revenue_upsell_recommendations_restaurant_generated",
        "revenue_upsell_recommendations",
        ["restaurant_id", "generated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_revenue_upsell_recommendations_restaurant_generated",
        table_name="revenue_upsell_recommendations",
    )
    op.drop_table("revenue_upsell_recommendations")

    op.drop_index(
        "ix_revenue_experiment_events_experiment_variant",
        table_name="revenue_experiment_events",
    )
    op.drop_index(
        "ix_revenue_experiment_events_restaurant_recorded",
        table_name="revenue_experiment_events",
    )
    op.drop_table("revenue_experiment_events")

    op.drop_index(
        "ix_revenue_experiments_restaurant_status",
        table_name="revenue_experiments",
    )
    op.drop_table("revenue_experiments")

    op.drop_index(
        "ix_revenue_control_policies_restaurant_id",
        table_name="revenue_control_policies",
    )
    op.drop_table("revenue_control_policies")
