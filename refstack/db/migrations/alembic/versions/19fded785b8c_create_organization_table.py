"""Create organization table.

Revision ID: 19fded785b8c
Revises: 319ee8fe47c7
Create Date: 2016-01-18 14:40:00

"""

# revision identifiers, used by Alembic.
revision = '19fded785b8c'
down_revision = '319ee8fe47c7'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'organization',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('group_id', sa.String(36), nullable=False),
        sa.Column('created_by_user', sa.String(128), nullable=False),
        sa.Column('properties', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
        sa.ForeignKeyConstraint(['created_by_user'], ['user.openid'], ),
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    """Downgrade DB."""
    op.drop_table('organization')
