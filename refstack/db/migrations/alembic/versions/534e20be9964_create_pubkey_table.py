"""Create user metadata table.

Revision ID: 534e20be9964
Revises: 2f178b0bf762
Create Date: 2015-07-03 13:26:29.138416

"""

# revision identifiers, used by Alembic.
revision = '534e20be9964'
down_revision = '2f178b0bf762'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'pubkeys',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('openid', sa.String(length=128),
                  nullable=False, index=True),
        sa.Column('format', sa.String(length=24), nullable=False),
        sa.Column('pubkey', sa.Text(), nullable=False),
        sa.Column('md5_hash', sa.String(length=32),
                  nullable=False, index=True),
        sa.Column('comment', sa.String(length=128)),
        sa.ForeignKeyConstraint(['openid'], ['user.openid'], ),
        mysql_charset=MYSQL_CHARSET
    )
    op.create_index('indx_meta_value', 'meta', ['value'], mysql_length=32)


def downgrade():
    """Downgrade DB."""
    op.drop_table('pubkeys')
