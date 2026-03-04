"""ux03 audit events timeline

Revision ID: f38a933ea2e0
Revises: 3649d637c9a4
Create Date: 2026-03-04 02:08:58.108123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f38a933ea2e0'
down_revision: Union[str, None] = '3649d637c9a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("actor_type", sa.String(length=30), nullable=False),
        sa.Column("actor_name", sa.String(length=255), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=150), nullable=False),
        sa.Column("detail", sa.String(length=1000), nullable=False),
        sa.Column("source_module", sa.String(length=100), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_entity_type_entity_id", "audit_events", ["entity_type", "entity_id"], unique=False)
    op.create_index("ix_audit_events_source_module", "audit_events", ["source_module"], unique=False)
    op.create_index("ix_audit_events_actor_type", "audit_events", ["actor_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_actor_type", table_name="audit_events")
    op.drop_index("ix_audit_events_source_module", table_name="audit_events")
    op.drop_index("ix_audit_events_entity_type_entity_id", table_name="audit_events")
    op.drop_table("audit_events")
