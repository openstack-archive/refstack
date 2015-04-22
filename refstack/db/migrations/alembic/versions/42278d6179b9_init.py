"""Init.

Revision ID: 42278d6179b9
Revises: None
Create Date: 2015-01-09 15:00:11.385580

"""

# revision identifiers, used by Alembic.
revision = '42278d6179b9'
down_revision = None
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    op.create_table(
        'test',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('cpid', sa.String(length=128), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset=MYSQL_CHARSET,
    )
    op.create_table(
        'meta',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('test_id', sa.String(length=36), nullable=False),
        sa.Column('meta_key', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
        sa.PrimaryKeyConstraint('_id'),
        sa.UniqueConstraint('test_id', 'meta_key'),
        mysql_charset=MYSQL_CHARSET
    )
    op.create_table(
        'results',
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer, default=0),
        sa.Column('_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('test_id', sa.String(length=36), nullable=False),
        sa.Column('name',
                  sa.String(length=512, collation='latin1_swedish_ci'),
                  nullable=True),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
        sa.PrimaryKeyConstraint('_id'),
        sa.UniqueConstraint('test_id', 'name'),
        # TODO(sslypushenko)
        # Constraint should turned on after duplication test uuids issue
        # will be fixed
        # sa.UniqueConstraint('test_id', 'uuid')
        mysql_charset=MYSQL_CHARSET
    )


def downgrade():
    """Downgrade DB."""
    op.drop_table('results')
    op.drop_table('meta')
    op.drop_table('test')
