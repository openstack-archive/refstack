"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
MYSQL_CHARSET = 'utf8'

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade():
    """Upgrade DB."""
    ${upgrades if upgrades else "pass"}


def downgrade():
    """Downgrade DB."""
    ${downgrades if downgrades else "pass"}
