"""Add product_version_id column to test.

Revision ID: 23843be3da52
Revises: 35bf54e2c13c
Create Date: 2016-07-30 18:15:52.429610
"""

# revision identifiers, used by Alembic.
revision = '23843be3da52'
down_revision = '35bf54e2c13c'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.add_column('test', sa.Column('product_version_id', sa.String(36),
                  nullable=True))
    op.create_foreign_key('fk_test_prod_version_id', 'test', 'product_version',
                          ['product_version_id'], ['id'])


def downgrade():
    """Downgrade DB."""
    op.drop_constraint('fk_test_prod_version_id', 'test', type_="foreignkey")
    op.drop_column('test', 'product_version_id')
