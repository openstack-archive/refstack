"""Create group table and group-user links table.

Revision ID: 319ee8fe47c7
Revises: 428e5aef5534
Create Date: 2016-01-15 16:34:00

"""

# revision identifiers, used by Alembic.
revision = '319ee8fe47c7'
down_revision = '428e5aef5534'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'group',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'user_to_group',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('created_by_user', sa.String(length=128), nullable=False),
        sa.Column('_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.String(36), nullable=False),
        sa.Column('user_openid', sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint('_id'),
        sa.ForeignKeyConstraint(['user_openid'], ['user.openid'], ),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    """Downgrade DB."""
    op.drop_table('user_to_group')
    op.drop_table('group')
