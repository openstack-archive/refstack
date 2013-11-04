"""from scratch

Revision ID: 3790aed42558
Revises: None
Create Date: 2013-10-30 03:52:16.922050

"""

# revision identifiers, used by Alembic.
revision = '3790aed42558'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cloud',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=60), nullable=True),
    sa.Column('endpoint', sa.String(length=120), nullable=True),
    sa.Column('test_user', sa.String(length=80), nullable=True),
    sa.Column('test_key', sa.String(length=80), nullable=True),
    sa.Column('admin_endpoint', sa.String(length=120), nullable=True),
    sa.Column('admin_user', sa.String(length=80), nullable=True),
    sa.Column('admin_key', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('endpoint')
    )
    op.create_table('vendor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vendor_name', sa.String(length=80), nullable=True),
    sa.Column('contact_email', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('contact_email'),
    sa.UniqueConstraint('vendor_name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=True),
    sa.Column('openid', sa.String(length=200), nullable=True),
    sa.Column('authorized', sa.Boolean(), nullable=True),
    sa.Column('su', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('openid')
    )
    op.create_table('test',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cloud_id', sa.Integer(), nullable=True),
    sa.Column('config', sa.String(length=4096), nullable=True),
    sa.ForeignKeyConstraint(['cloud_id'], ['cloud.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('blob', sa.Binary(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=1024), nullable=True),
    sa.Column('finished', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_status')
    op.drop_table('test_results')
    op.drop_table('test')
    op.drop_table('user')
    op.drop_table('vendor')
    op.drop_table('cloud')
    ### end Alembic commands ###
