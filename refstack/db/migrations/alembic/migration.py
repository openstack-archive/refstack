# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Implementation of Alembic commands."""
import alembic
import alembic.migration as alembic_migration
from oslo_config import cfg
from refstack.db.sqlalchemy import api as db_api
from refstack.db.migrations.alembic import utils

CONF = cfg.CONF


def version():
    """Current database version.

    :returns: Database version
    :type: string
    """
    engine = db_api.get_engine()
    with engine.connect() as conn:
        conf_table = getattr(CONF, 'version_table')
        utils.recheck_alembic_table(conn)
        context = alembic_migration.MigrationContext.configure(
            conn, opts={'version_table': conf_table})
        return context.get_current_revision()


def upgrade(revision):
    """Upgrade database.

    :param version: Desired database version
    :type version: string
    """
    return alembic.command.upgrade(utils.alembic_config(), revision or 'head')


def downgrade(revision):
    """Downgrade database.

    :param version: Desired database version
    :type version: string
    """
    return alembic.command.downgrade(utils.alembic_config(),
                                     revision or 'base')


def stamp(revision):
    """Stamp database with provided revision.

    Don't run any migrations.

    :param revision: Should match one from repository or head - to stamp
    database with most recent revision
    :type revision: string
    """
    return alembic.command.stamp(utils.alembic_config(), revision or 'head')


def revision(message=None, autogenerate=False):
    """Create template for migration.

    :param message: Text that will be used for migration title
    :type message: string
    :param autogenerate: If True - generates diff based on current database
    state
    :type autogenerate: bool
    """
    return alembic.command.revision(utils.alembic_config(),
                                    message, autogenerate)
