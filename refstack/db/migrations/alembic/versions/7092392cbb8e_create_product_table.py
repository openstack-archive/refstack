"""Create product table.

Revision ID: 7092392cbb8e
Revises: 19fded785b8c
Create Date: 2016-01-18 16:10:00

"""

# revision identifiers, used by Alembic.
revision = '7092392cbb8e'
down_revision = '19fded785b8c'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'product',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user', sa.String(128), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('product_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('product_type', sa.Integer(), nullable=False),
        sa.Column('public', sa.Boolean(), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('properties', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['created_by_user'], ['user.openid'], ),
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    """Downgrade DB."""
    op.drop_table('product')
