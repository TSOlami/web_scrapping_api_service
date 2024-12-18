"""add image_url column

Revision ID: 001
Revises: 
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('scholarships', sa.Column('image_url', sa.String(500), nullable=True))

def downgrade() -> None:
    op.drop_column('scholarships', 'image_url') 
    