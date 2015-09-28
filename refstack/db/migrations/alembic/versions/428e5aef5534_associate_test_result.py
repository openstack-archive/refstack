"""Associate test results to users.

Revision ID: 428e5aef5534
Revises: 534e20be9964
Create Date: 2015-11-03 00:51:34.096598

"""

# revision identifiers, used by Alembic.
revision = '428e5aef5534'
down_revision = '534e20be9964'
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Upgrade DB."""
    conn = op.get_bind()
    res = conn.execute("select openid,format,pubkey from pubkeys")
    results = res.fetchall()

    # Get public key to user mappings.
    pubkeys = {}
    for result in results:
        pubkeys[result[1] + " " + result[2]] = result[0]

    res = conn.execute("select test_id,value from meta where "
                       "meta_key='public_key'")
    results = res.fetchall()

    for result in results:
        test_id = result[0]
        if result[1] in pubkeys:
            openid = pubkeys[result[1]]
            conn.execute(sa.text("update meta set meta_key='user', "
                                 "value=:value where "
                                 "test_id=:testid and meta_key='public_key'"
                                 ),
                         value=openid, testid=test_id)


def downgrade():
    """Downgrade DB."""
    pass
