"""ux03 exception workflow fields

Revision ID: 3649d637c9a4
Revises: ab57cd3db3df
Create Date: 2026-03-04 01:54:33.664044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3649d637c9a4'
down_revision: Union[str, None] = 'ab57cd3db3df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("owner", sa.String(length=100), nullable=True))
    op.add_column(
        "alerts",
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
    )
    op.add_column(
        "alerts",
        sa.Column("sla_status", sa.String(length=30), nullable=False, server_default="on_track"),
    )
    op.add_column("alerts", sa.Column("sla_minutes", sa.Integer(), nullable=True))
    op.add_column("alerts", sa.Column("due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("alerts", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("alerts", sa.Column("resolved_by", sa.Integer(), nullable=True))

    op.create_foreign_key(
        "fk_alerts_resolved_by_users",
        "alerts",
        "users",
        ["resolved_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_alerts_status", "alerts", ["status"], unique=False)
    op.create_index("ix_alerts_owner", "alerts", ["owner"], unique=False)

    # Backfill workflow defaults for existing alerts.
    op.execute(
        """
        UPDATE alerts
        SET status = CASE WHEN is_read THEN 'resolved' ELSE 'open' END,
            sla_status = CASE WHEN is_read THEN 'resolved' ELSE 'on_track' END,
            sla_minutes = CASE
                WHEN severity = 'critical' THEN 30
                WHEN severity = 'warning' THEN 120
                ELSE 480
            END,
            owner = CASE module
                WHEN 'billing' THEN 'Finance'
                WHEN 'inventory' THEN 'Supply'
                WHEN 'reservations' THEN 'Service'
                WHEN 'kitchen' THEN 'Kitchen'
                WHEN 'workforce' THEN 'Operations'
                WHEN 'marketing' THEN 'Growth'
                ELSE 'Operations'
            END,
            due_at = created_at + (
                CASE
                    WHEN severity = 'critical' THEN INTERVAL '30 minutes'
                    WHEN severity = 'warning' THEN INTERVAL '120 minutes'
                    ELSE INTERVAL '480 minutes'
                END
            )
        """
    )
    op.execute(
        """
        UPDATE alerts
        SET resolved_at = updated_at
        WHERE status = 'resolved'
        """
    )

    op.alter_column("alerts", "status", server_default=None)
    op.alter_column("alerts", "sla_status", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_alerts_owner", table_name="alerts")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_constraint("fk_alerts_resolved_by_users", "alerts", type_="foreignkey")
    op.drop_column("alerts", "resolved_by")
    op.drop_column("alerts", "resolved_at")
    op.drop_column("alerts", "due_at")
    op.drop_column("alerts", "sla_minutes")
    op.drop_column("alerts", "sla_status")
    op.drop_column("alerts", "status")
    op.drop_column("alerts", "owner")
