"""Add Product version table.

Also product_ref_id is removed from the product table.

Revision ID: 35bf54e2c13c
Revises: 709452f38a5c
Create Date: 2016-07-30 17:59:57.912306

"""

# revision identifiers, used by Alembic.
revision = '35bf54e2c13c'
down_revision = '709452f38a5c'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'product_version',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user', sa.String(128), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('product_id', sa.String(36), nullable=False),
        sa.Column('version', sa.String(length=36), nullable=True),
        sa.Column('cpid', sa.String(length=36)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.ForeignKeyConstraint(['created_by_user'], ['user.openid'], ),
        sa.UniqueConstraint('product_id', 'version', name='prod_ver_uc'),
        mysql_charset=MYSQL_CHARSET
    )
    op.drop_column('product', 'product_ref_id')


def downgrade():
    """Downgrade DB."""
    op.drop_table('product_version')
    op.add_column('product',
                  sa.Column('product_ref_id', sa.String(36), nullable=True))
