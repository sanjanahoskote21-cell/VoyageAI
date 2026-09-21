"""add source field to places

Revision ID: f1be5fbfdd90
Revises: e8d1af049731
Create Date: 2026-08-19 17:17:57.499768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1be5fbfdd90'
down_revision: Union[str, Sequence[str], None] = 'e8d1af049731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('places', sa.Column('source', sa.String(), nullable=False, server_default='seeded'))

def downgrade():
    op.drop_column('places', 'source')