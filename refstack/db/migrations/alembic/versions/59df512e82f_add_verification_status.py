"""Add verification_status field to test.

Revision ID: 59df512e82f
Revises: 23843be3da52
Create Date: 2016-09-26 11:51:08.955006

"""

# revision identifiers, used by Alembic.
revision = '59df512e82f'
down_revision = '23843be3da52'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.add_column('test', sa.Column('verification_status',
                                    sa.Integer,
                                    nullable=False,
                                    default=0))


def downgrade():
    """Downgrade DB."""
    op.drop_column('test', 'verification_status')
