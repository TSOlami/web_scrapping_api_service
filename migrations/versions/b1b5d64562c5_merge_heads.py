"""Merge heads

Revision ID: b1b5d64562c5
Revises: 1c7e84d3cfdb, 76ee460a4d4e
Create Date: 2024-12-23 18:48:34.779673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1b5d64562c5'
down_revision: Union[str, None] = ('1c7e84d3cfdb', '76ee460a4d4e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
