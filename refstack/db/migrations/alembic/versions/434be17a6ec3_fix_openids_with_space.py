"""Fix openids with spaces.

A change in the openstackid naming made is so IDs with spaces
are trimmed, so %20 are no longer in the openid url. This migration
will replace any '%20' with a '.' in each openid.

Revision ID: 434be17a6ec3
Revises: 59df512e82f
Create Date: 2017-03-23 12:20:08.219294

"""

# revision identifiers, used by Alembic.
revision = '434be17a6ec3'
down_revision = '59df512e82f'
MYSQL_CHARSET = 'utf8'

from alembic import op


def upgrade():
    """Upgrade DB."""
    conn = op.get_bind()
    # Need to disable FOREIGN_KEY_CHECKS as a lot of tables reference the
    # openid in the user table.
    conn.execute("SET FOREIGN_KEY_CHECKS=0")
    res = conn.execute("select * from user where openid LIKE '%%\%%20%%'")
    results = res.fetchall()
    for user in results:
        old_openid = user[5]
        new_openid = user[5].replace('%20', '.')

        # Remove instances of the new openid so the old one can take
        # its place.
        query = "delete from user where openid='%s'" % (new_openid)
        conn.execute(query.replace('%', '%%'))

        # Update the openid.
        query = ("update user set openid='%s' where openid='%s'" %
                 (new_openid, old_openid))
        conn.execute(query.replace('%', '%%'))

    # Update all usage of %20 in all openid references using MySQL Replace.
    conn.execute("update meta set value = "
                 "REPLACE (value, '%%20', '.')")
    conn.execute("update pubkeys set openid = "
                 "REPLACE (openid, '%%20', '.')")
    conn.execute("update organization set created_by_user = "
                 "REPLACE (created_by_user, '%%20', '.')")
    conn.execute("update product set created_by_user = "
                 "REPLACE (created_by_user, '%%20', '.')")
    conn.execute("update product_version set created_by_user = "
                 "REPLACE (created_by_user, '%%20', '.')")
    conn.execute("update user_to_group set created_by_user = "
                 "REPLACE (created_by_user, '%%20', '.')")
    conn.execute("update user_to_group set user_openid = "
                 "REPLACE (user_openid, '%%20', '.')")

    conn.execute("SET FOREIGN_KEY_CHECKS=1")


def downgrade():
    """Downgrade DB."""
    pass
