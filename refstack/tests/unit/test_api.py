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

"""Tests for API's controllers"""

import mock
from oslotest import base

from refstack.api.controllers import root
from refstack.api.controllers import v1


class RootControllerTestCase(base.BaseTestCase):

    def test_index(self):
        controller = root.RootController()
        result = controller.index()
        self.assertEqual(result, {'Root': 'OK'})


class ResultsControllerTestCase(base.BaseTestCase):

    def setUp(self):
        super(ResultsControllerTestCase, self).setUp()
        self.validator = mock.Mock()
        self.controller = v1.ResultsController(self.validator)

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.get_test_results')
    def test_get(self, mock_get_test_res, mock_get_test):
        self.validator.assert_id.return_value = True

        test_info = mock.Mock()
        test_info.cpid = 'foo'
        test_info.created_at = 'bar'
        test_info.duration_seconds = 999
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [('test1',), ('test2',), ('test3',)]

        actual_result = self.controller.get_one('fake_arg')
        expected_result = {
            'cpid': 'foo',
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2', 'test3']
        }

        self.assertEqual(actual_result, expected_result)
        mock_get_test_res.assert_called_once_with('fake_arg')
        mock_get_test.assert_called_once_with('fake_arg')
        self.validator.assert_id.assert_called_once_with('fake_arg')

    @mock.patch('refstack.db.store_results')
    @mock.patch('pecan.response')
    @mock.patch('refstack.common.validators.safe_load_json_body')
    def test_post(self, mock_safe_load, mock_response, mock_store_results):
        mock_safe_load.return_value = 'fake_item'
        mock_store_results.return_value = 'fake_test_id'

        result = self.controller.post()

        self.assertEqual(result, {'test_id': 'fake_test_id'})
        self.assertEqual(mock_response.status, 201)
        mock_safe_load.assert_called_once_with(self.validator)
        mock_store_results.assert_called_once_with('fake_item')

    @mock.patch('pecan.abort')
    @mock.patch('refstack.db.get_test')
    def test_get_item_failed(self, mock_get_test, mock_abort):
        mock_get_test.return_value = None
        mock_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get_item,
                          'fake_id')

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.get_test_results')
    def test_get_item(self, mock_get_test_res, mock_get_test):
        test_info = mock.Mock()
        test_info.cpid = 'foo'
        test_info.created_at = 'bar'
        test_info.duration_seconds = 999
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [('test1',), ('test2',), ('test3',)]

        actual_result = self.controller.get_item('fake_id')
        expected_result = {
            'cpid': 'foo',
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2', 'test3']
        }
        self.assertEqual(actual_result, expected_result)
        mock_get_test_res.assert_called_once_with('fake_id')
        mock_get_test.assert_called_once_with('fake_id')

    @mock.patch('refstack.db.store_results')
    def test_store_item(self, mock_store_item):
        mock_store_item.return_value = 'fake_result'
        result = self.controller.store_item('fake_item')
        self.assertEqual(result, {'test_id': 'fake_result'})
        mock_store_item.assert_called_once_with('fake_item')


class RestControllerWithValidationTestCase(base.BaseTestCase):

    def setUp(self):
        super(RestControllerWithValidationTestCase, self).setUp()
        self.validator = mock.Mock()
        self.controller = v1.RestControllerWithValidation(self.validator)

    @mock.patch('pecan.response')
    @mock.patch('refstack.common.validators.safe_load_json_body')
    def test_post(self, mock_safe_load, mock_response):
        mock_safe_load.return_value = 'fake_item'
        self.controller.store_item = mock.Mock(return_value='fake_id')

        result = self.controller.post()

        self.assertEqual(result, 'fake_id')
        self.assertEqual(mock_response.status, 201)
        mock_safe_load.assert_called_once_with(self.validator)
        self.controller.store_item.assert_called_once_with('fake_item')

    def test_get_one_return_item(self):
        self.validator.assert_id.return_value = True
        self.controller.get_item = mock.Mock(return_value='fake_item')

        result = self.controller.get_one('fake_arg')

        self.assertEqual(result, 'fake_item')
        self.validator.assert_id.assert_called_once_with('fake_arg')
        self.controller.get_item.assert_called_once_with(item_id='fake_arg')

    def test_get_one_return_schema(self):
        self.validator.assert_id.return_value = False
        self.validator.schema = 'fake_schema'
        result = self.controller.get_one('schema')
        self.assertEqual(result, 'fake_schema')

    @mock.patch('pecan.abort')
    def test_get_one_aborut(self, mock_abort):
        self.validator.assert_id.return_value = False
        self.controller.get_one('fake_arg')
        mock_abort.assert_called_once_with(404)
