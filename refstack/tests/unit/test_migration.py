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

"""Tests for refstack's migrations."""

import alembic
import mock
from oslotest import base

from refstack.db import migration
from refstack.db.migrations.alembic import migration as alembic_migration


class AlembicConfigTestCase(base.BaseTestCase):

    @mock.patch('alembic.config.Config')
    @mock.patch('os.path.join')
    def test_alembic_config(self, os_join, alembic_config):
        os_join.return_value = 'fake_path'
        alembic_config.return_value = 'fake_config'
        result = alembic_migration._alembic_config()
        self.assertEqual(result, 'fake_config')
        alembic_config.assert_called_once_with('fake_path')


class MigrationTestCase(base.BaseTestCase):
    """Test case for alembic's migrations API."""

    def setUp(self):
        super(MigrationTestCase, self).setUp()
        self.config_patcher = mock.patch(
            'refstack.db.migrations.alembic.migration._alembic_config')
        self.config = self.config_patcher.start()
        self.config.return_value = 'fake_config'
        self.addCleanup(self.config_patcher.stop)

    @mock.patch.object(alembic.migration.MigrationContext, 'configure',
                       mock.Mock())
    def test_version(self):
        context = mock.Mock()
        context.get_current_revision = mock.Mock()
        alembic.migration.MigrationContext.configure.return_value = context
        with mock.patch('refstack.db.sqlalchemy.api.get_engine') as get_engine:
            engine = mock.Mock()
            engine.connect = mock.MagicMock()
            get_engine.return_value = engine
            migration.version()
            context.get_current_revision.assert_called_once_with()
            engine.connect.assert_called_once_with()

    @mock.patch('alembic.command.upgrade')
    def test_upgrade(self, upgrade):
        migration.upgrade('some_revision')
        upgrade.assert_called_once_with('fake_config', 'some_revision')

    @mock.patch('alembic.command.upgrade')
    def test_upgrade_without_revision(self, upgrade):
        migration.upgrade(None)
        upgrade.assert_called_once_with('fake_config', 'head')

    @mock.patch('alembic.command.downgrade')
    def test_downgrade(self, downgrade):
        migration.downgrade('some_revision')
        downgrade.assert_called_once_with('fake_config', 'some_revision')

    @mock.patch('alembic.command.downgrade')
    def test_downgrade_without_revision(self, downgrade):
        migration.downgrade(None)
        downgrade.assert_called_once_with('fake_config', 'base')

    @mock.patch('alembic.command.stamp')
    def test_stamp(self, stamp):
        migration.stamp('some_revision')
        stamp.assert_called_once_with('fake_config', 'some_revision')

    @mock.patch('alembic.command.stamp')
    def test_stamp_without_revision(self, stamp):
        migration.stamp(None)
        stamp.assert_called_once_with('fake_config', 'head')

    @mock.patch('alembic.command.revision')
    def test_revision(self, revision):
        migration.revision('some_message', True)
        revision.assert_called_once_with('fake_config', 'some_message', True)
