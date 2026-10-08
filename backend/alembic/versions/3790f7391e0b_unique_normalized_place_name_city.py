"""unique normalized place name city

Revision ID: 3790f7391e0b
Revises: f1be5fbfdd90
Create Date: 2026-10-08 20:33:43.123296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3790f7391e0b'
down_revision: Union[str, Sequence[str], None] = 'f1be5fbfdd90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_places_name_city_norm",
        "places",
        [sa.text("lower(btrim(name))"), sa.text("lower(btrim(city))")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_places_name_city_norm", table_name="places")
