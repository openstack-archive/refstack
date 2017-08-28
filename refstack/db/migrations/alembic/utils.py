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
"""Utilities used in the implementation of Alembic commands."""
import os

from alembic import config as alembic_conf
from alembic.operations import Operations
import alembic.migration as alembic_migration
from collections import Iterable
from oslo_config import cfg
from sqlalchemy import text


CONF = cfg.CONF


def alembic_config():
    """Initialize config objext from .ini file.

    :returns: config object.
    :type: object
    """
    path = os.path.join(os.path.dirname(__file__), os.pardir, 'alembic.ini')
    config = alembic_conf.Config(path)
    return config


def get_table_version(conn, version_table_name):
    """Get table version.

    :param engine: Initialized alembic engine object.
    :param version_table_name: Version table name to check.
    :type engine: object
    :type version_table_name: string
    :returns: string
    """
    if not version_table_name:
        return None
    context = alembic_migration.MigrationContext.configure(
        conn, opts={'version_table': version_table_name})
    return context.get_current_revision()


def get_db_tables(conn):
    """Get current and default table values from the db.

    :param engine: Initialized alembic engine object.
    :type engine: object
    :returns: tuple
    """
    query = text("SELECT TABLE_NAME from information_schema.tables\
                  WHERE TABLE_NAME\
                  LIKE '%alembic_version%'\
                  AND table_schema = 'refstack'")
    context = alembic_migration.MigrationContext.configure(conn)
    op = Operations(context)
    connection = op.get_bind()
    search = connection.execute(query)
    result = search.fetchall()
    if isinstance(result, Iterable):
        result = [table[0] for table in result]
    else:
        result = None
    # if there is more than one version table, modify the
    # one that does not have the default name, because subunit2sql uses the
    # default name.
    if result:
        current_name =\
            next((table for table in result if table != "alembic_version"),
                 result[0])
        current_name = current_name.decode('utf-8')
        current_version = get_table_version(conn, current_name)
        default_name =\
            next((table for table in result
                  if table == "alembic_version"), None)
        default_version = get_table_version(conn, default_name)
        if len(result) > 1 and not current_version:
            if not default_name:
                # this is the case where there is more than one
                # nonstandard-named alembic table, and no default
                current_name = next((table for table in result
                                     if table != current_name),
                                    result[0])
                current_name = current_name.decode('utf-8')
            elif current_name:
                # this is the case where the current-named table
                # exists, but is empty
                current_name = default_name
                current_version = default_version
        current_table = (current_name, current_version)
        default_table = (default_name, default_version)
    else:
        default_table = (None, None)
        current_table = default_table
    return current_table, default_table


def recheck_alembic_table(conn):
    """check and update alembic version table.

    Should check current alembic version table against conf and rename the
    existing table if the two values don't match.
    """
    conf_table = getattr(CONF, 'version_table')
    conf_table_version = get_table_version(conn, conf_table)
    current_table, default_table = get_db_tables(conn)
    if current_table[0]:
        if current_table[0] != conf_table:
            context = alembic_migration.MigrationContext.configure(conn)
            op = Operations(context)
            if conf_table and not conf_table_version:
                # make sure there is not present-but-empty table
                # that will prevent us from renaming the current table
                op.drop_table(conf_table)
            op.rename_table(current_table[0], conf_table)
