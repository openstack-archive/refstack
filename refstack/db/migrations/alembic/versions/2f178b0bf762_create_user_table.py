"""Create user table.

Revision ID: 2f178b0bf762
Revises: 42278d6179b9
Create Date: 2015-05-12 12:15:43.810938

"""

# revision identifiers, used by Alembic.
revision = '2f178b0bf762'
down_revision = '42278d6179b9'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'user',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('openid', sa.String(length=128),
                  nullable=False, unique=True),
        sa.Column('email', sa.String(length=128)),
        sa.Column('fullname', sa.String(length=128)),
        sa.PrimaryKeyConstraint('_id'),
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    """Downgrade DB."""
    op.drop_table('user')
