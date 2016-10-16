"""Rename product_id to product_ref_id.

Revision ID: 709452f38a5c
Revises: 7093ca478d35
Create Date: 2016-06-27 13:10:00

"""

# revision identifiers, used by Alembic.
revision = '709452f38a5c'
down_revision = '7093ca478d35'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.alter_column('product', 'product_id', new_column_name='product_ref_id',
                    type_=sa.String(36))


def downgrade():
    """Downgrade DB."""
    op.alter_column('product', 'product_ref_id', new_column_name='product_id',
                    type_=sa.String(36))
