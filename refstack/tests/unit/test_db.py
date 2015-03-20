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

"""Tests for database."""

import six
import mock
from oslo_config import fixture as config_fixture
from oslotest import base

from refstack import db
from refstack.api import constants as api_const
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

    @mock.patch.object(api, 'get_test_records')
    def test_get_test_records(self, mock_db):
        filters = mock.Mock()
        db.get_test_records(1, 2, filters)
        mock_db.assert_called_once_with(1, 2, filters)

    @mock.patch.object(api, 'get_test_records_count')
    def test_get_test_records_count(self, mock_db):
        filters = mock.Mock()
        db.get_test_records_count(filters)
        mock_db.assert_called_once_with(filters)


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

    @mock.patch('oslo_db.sqlalchemy.session.EngineFacade.from_config')
    def test_create_facade_lazily(self, session):
        session.return_value = 'fake_session'
        result = api._create_facade_lazily()
        self.assertEqual(result, 'fake_session')


class DBBackendTestCase(base.BaseTestCase):
    """Test case for database backend."""

    def setUp(self):
        super(DBBackendTestCase, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

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

    @mock.patch('refstack.db.sqlalchemy.models.Test')
    def test_apply_filters_for_query(self, mock_model):
        query = mock.Mock()
        mock_model.created_at = six.text_type()

        filters = {
            api_const.START_DATE: 'fake1',
            api_const.END_DATE: 'fake2',
            api_const.CPID: 'fake3'
        }

        result = api._apply_filters_for_query(query, filters)

        query.filter.assert_called_once_with(mock_model.created_at >=
                                             filters[api_const.START_DATE])

        query = query.filter.return_value
        query.filter.assert_called_once_with(mock_model.created_at <=
                                             filters[api_const.END_DATE])

        query = query.filter.return_value
        query.filter.assert_called_once_with(mock_model.cpid ==
                                             filters[api_const.CPID])

        query = query.filter.return_value
        self.assertEqual(result, query)

    @mock.patch.object(api, '_apply_filters_for_query')
    @mock.patch.object(api, 'get_session')
    @mock.patch('refstack.db.sqlalchemy.models.Test')
    def test_get_test_records(self, mock_model,
                              mock_get_session,
                              mock_apply):

        per_page = 9000
        filters = {
            api_const.START_DATE: 'fake1',
            api_const.END_DATE: 'fake2',
            api_const.CPID: 'fake3'
        }

        session = mock_get_session.return_value
        first_query = session.query.return_value
        second_query = mock_apply.return_value
        ordered_query = second_query.order_by.return_value
        query_with_offset = ordered_query.offset.return_value
        query_with_offset.limit.return_value = 'fake_uploads'

        result = api.get_test_records(2, per_page, filters)

        mock_get_session.assert_called_once_with()
        session.query.assert_called_once_with(mock_model.id,
                                              mock_model.created_at,
                                              mock_model.cpid)
        mock_apply.assert_called_once_with(first_query, filters)
        second_query.order_by.\
            assert_called_once_with(mock_model.created_at.desc())

        self.assertEqual(result, 'fake_uploads')
        ordered_query.offset.assert_called_once_with(per_page)
        query_with_offset.limit.assert_called_once_with(per_page)

    @mock.patch.object(api, '_apply_filters_for_query')
    @mock.patch.object(api, 'get_session')
    @mock.patch('refstack.db.sqlalchemy.models.Test')
    def test_get_test_records_count(self, mock_model,
                                    mock_get_session,
                                    mock_apply):

        filters = mock.Mock()
        session = mock_get_session.return_value
        query = session.query.return_value
        apply_result = mock_apply.return_value
        apply_result.count.return_value = 999

        result = api.get_test_records_count(filters)
        self.assertEqual(result, 999)

        session.query.assert_called_once_with(mock_model.id)
        mock_apply.assert_called_once_with(query, filters)
        apply_result.count.assert_called_once_with()
