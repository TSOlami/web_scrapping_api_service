# -*- coding: utf-8 -*-
"""Allow degree_level to be nullable"""

# revision identifiers, used by Alembic.
revision = '76ee460a4d4e'
down_revision = '281d771498e9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Empty upgrade function, nothing will be applied here
    pass

def downgrade():
    # Empty downgrade function, nothing will be reverted here
    pass
