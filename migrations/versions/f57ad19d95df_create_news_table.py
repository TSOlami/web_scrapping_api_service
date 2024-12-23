"""Create News table

Revision ID: f57ad19d95df
Revises: 002
Create Date: 2024-12-23 12:35:21.986670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f57ad19d95df'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scholarships', 'requirements',
               existing_type=mysql.TEXT(),
               type_=sa.JSON(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scholarships', 'requirements',
               existing_type=sa.JSON(),
               type_=mysql.TEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###