"""added_alt_user

Revision ID: 121ee191d348
Revises: 2d1f3e3cd357
Create Date: 2014-04-07 11:43:51.800255

"""

# revision identifiers, used by Alembic.
revision = '121ee191d348'
down_revision = '2d1f3e3cd357'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'cloud',
        sa.Column('alt_user', sa.String(length=80), nullable=True))


def downgrade():
    op.drop_column('cloud', 'alt_user')
