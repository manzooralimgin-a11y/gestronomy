"""add table layout fields

Revision ID: d4e5f6g7h8i9
Revises: bf1832e7e1be
Create Date: 2026-03-14 02:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'bf1832e7e1be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tables', sa.Column('rotation', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('tables', sa.Column('width', sa.Float(), nullable=False, server_default='1.0'))
    op.add_column('tables', sa.Column('height', sa.Float(), nullable=False, server_default='1.0'))


def downgrade() -> None:
    op.drop_column('tables', 'height')
    op.drop_column('tables', 'width')
    op.drop_column('tables', 'rotation')
