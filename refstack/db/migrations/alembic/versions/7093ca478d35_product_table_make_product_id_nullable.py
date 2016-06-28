"""Make product_id nullable in product table.

Revision ID: 7093ca478d35
Revises: 7092392cbb8e
Create Date: 2016-05-12 13:10:00

"""

# revision identifiers, used by Alembic.
revision = '7093ca478d35'
down_revision = '7092392cbb8e'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.alter_column('product', 'product_id', nullable=True,
                    type_=sa.String(36))


def downgrade():
    """Downgrade DB."""
    pass
