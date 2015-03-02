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

"""Tests for database API."""

import six
import mock
from oslotest import base

from refstack import db
from refstack.db.sqlalchemy import api


class DBAPITestCase(base.BaseTestCase):
    """Test case for database API."""

    @mock.patch.object(api, 'store_results')
    def test_store_results(self, mock_store_results):
        db.store_results('fake_results')
        mock_store_results.assert_called_once_with('fake_results')

    @mock.patch.object(api, 'get_test')
    def test_get_test(self, mock_get_test):
        db.get_test(12345)
        mock_get_test.assert_called_once_with(12345)

    @mock.patch.object(api, 'get_test_results')
    def test_get_test_results(self, mock_get_test_results):
        db.get_test_results(12345)
        mock_get_test_results.assert_called_once_with(12345)


class DBHelpersTestCase(base.BaseTestCase):
    """Test case for database backend helpers."""

    @mock.patch.object(api, '_create_facade_lazily')
    def test_get_engine(self, mock_create_facade):
        facade = mock_create_facade.return_value
        facade.get_engine = mock.Mock(return_value='fake_engine')

        result = api.get_engine()
        mock_create_facade.assert_called_once_with()
        facade.get_engine.assert_called_once_with()
        self.assertEqual(result, 'fake_engine')

    @mock.patch.object(api, '_create_facade_lazily')
    def test_get_session(self, mock_create_facade):
        facade = mock_create_facade.return_value
        facade.get_session = mock.Mock(return_value='fake_session')

        fake_kwargs = {'foo': 'bar'}
        result = api.get_session(**fake_kwargs)

        mock_create_facade.assert_called_once_with()
        facade.get_session.assert_called_once_with(**fake_kwargs)
        self.assertEqual(result, 'fake_session')


class DBBackendTestCase(base.BaseTestCase):
    """Test case for database backend."""

    @mock.patch.object(api, 'get_session')
    @mock.patch('refstack.db.sqlalchemy.models.TestResults')
    @mock.patch('refstack.db.sqlalchemy.models.Test')
    @mock.patch('uuid.uuid4')
    def test_store_results(self, mock_uuid, mock_test,
                           mock_test_result, mock_get_session):
        fake_tests_result = {
            'cpid': 'foo',
            'duration_seconds': 10,
            'results': [
                {'name': 'tempest.some.test'},
                {'name': 'tempest.test', 'uid': '12345678'}
            ]
        }
        _id = 12345

        mock_uuid.return_value = _id
        test = mock_test.return_value
        test.save = mock.Mock()

        session = mock_get_session.return_value
        session.begin = mock.MagicMock()

        test_result = mock_test_result.return_value
        test_result.save = mock.Mock()

        test_id = api.store_results(fake_tests_result)

        mock_test.assert_called_once_with()
        mock_get_session.assert_called_once_with()
        test.save.assert_called_once_with(session)
        session.begin.assert_called_once_with()

        self.assertEqual(test_id, six.text_type(_id))
        self.assertEqual(test.id, six.text_type(_id))
        self.assertEqual(test.cpid, fake_tests_result['cpid'])
        self.assertEqual(test.duration_seconds,
                         fake_tests_result['duration_seconds'])
        self.assertEqual(mock_test_result.call_count,
                         len(fake_tests_result['results']))
        self.assertEqual(test_result.save.call_count,
                         len(fake_tests_result['results']))

    @mock.patch.object(api, 'get_session')
    @mock.patch('refstack.db.sqlalchemy.models.Test')
    def test_get_test(self, mock_test, mock_get_session):
        session = mock_get_session.return_value
        session.query = mock.Mock()
        query = session.query.return_value
        query.filter_by = mock.Mock()
        filter_by = query.filter_by.return_value
        expected_result = 'fake_test_info'
        filter_by.first = mock.Mock(return_value=expected_result)

        test_id = 'fake_id'
        actual_result = api.get_test(test_id)

        mock_get_session.assert_called_once_with()
        session.query.assert_called_once_with(mock_test)
        query.filter_by.assert_called_once_with(id=test_id)
        filter_by.first.assert_called_once_with()
        self.assertEqual(expected_result, actual_result)

    @mock.patch.object(api, 'get_session')
    @mock.patch('refstack.db.sqlalchemy.models.TestResults')
    def test_get_test_results(self, mock_test_result, mock_get_session):
        mock_test_result.name = mock.Mock()

        session = mock_get_session.return_value
        session.query = mock.Mock()
        query = session.query.return_value
        query.filter_by = mock.Mock()
        filter_by = query.filter_by.return_value
        expected_result = 'fake_test_results'
        filter_by.all = mock.Mock(return_value=expected_result)

        test_id = 'fake_id'
        actual_result = api.get_test_results(test_id)

        mock_get_session.assert_called_once_with()
        session.query.assert_called_once_with(mock_test_result.name)
        query.filter_by.assert_called_once_with(test_id=test_id)
        filter_by.all.assert_called_once_with()
        self.assertEqual(expected_result, actual_result)
