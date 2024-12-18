"""add description column

Revision ID: 002
Revises: 001_add_image_url_column
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('scholarships', sa.Column('description', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('scholarships', 'description')
    