"""empty message

Revision ID: 449461dbc725
Revises: 59e15d864941
Create Date: 2013-11-26 16:57:16.062788

"""

# revision identifiers, used by Alembic.
revision = '449461dbc725'
down_revision = '59e15d864941'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'apikey',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=60), nullable=True),
        sa.Column('key', sa.String(length=200), nullable=True),
        sa.Column('openid', sa.String(length=200), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_Table('apikey')
