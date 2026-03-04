"""ag01 service autopilot predictions

Revision ID: 620206e756c2
Revises: f38a933ea2e0
Create Date: 2026-03-04 02:11:56.540824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '620206e756c2'
down_revision: Union[str, None] = 'f38a933ea2e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service_autopilot_predictions",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("table_id", sa.Integer(), nullable=True),
        sa.Column("horizon_minutes", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("target_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("predicted_wait_min", sa.Float(), nullable=False),
        sa.Column("staffing_pressure_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("actual_wait_min", sa.Float(), nullable=True),
        sa.Column("error_abs_min", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["table_id"], ["tables.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_service_autopilot_predictions_restaurant_target",
        "service_autopilot_predictions",
        ["restaurant_id", "target_time"],
        unique=False,
    )
    op.create_index(
        "ix_service_autopilot_predictions_table_generated",
        "service_autopilot_predictions",
        ["table_id", "generated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_autopilot_predictions_table_generated",
        table_name="service_autopilot_predictions",
    )
    op.drop_index(
        "ix_service_autopilot_predictions_restaurant_target",
        table_name="service_autopilot_predictions",
    )
    op.drop_table("service_autopilot_predictions")
