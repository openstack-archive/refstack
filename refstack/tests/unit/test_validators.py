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

"""Tests for validators."""

import json

import jsonschema
import mock
from oslotest import base

from refstack.common import validators


class ValidatorsTestCase(base.BaseTestCase):
    """Test case for validator's helpers."""

    def test_is_uuid(self):
        self.assertTrue(validators.is_uuid('12345678123456781234567812345678'))

    def test_is_uuid_fail(self):
        self.assertFalse(validators.is_uuid('some_string'))

    def test_checker_uuid(self):
        value = validators.checker_uuid('12345678123456781234567812345678')
        self.assertTrue(value)

    def test_checker_uuid_fail(self):
        self.assertFalse(validators.checker_uuid('some_string'))


class TestResultValidatorTestCase(base.BaseTestCase):
    """Test case for database TestResultValidator."""

    FAKE_TESTS_RESULTS_JSON = json.dumps({
        'cpid': 'foo',
        'duration_seconds': 10,
        'results': [
            {'name': 'tempest.some.test'},
            {'name': 'tempest.test', 'uid': '12345678'}
        ]
    })

    def setUp(self):
        super(TestResultValidatorTestCase, self).setUp()
        self.validator = validators.TestResultValidator()

    def test_assert_id(self):
        value = self.validator.assert_id('12345678123456781234567812345678')
        self.assertTrue(value)

    def test_assert_id_fail(self):
        self.assertFalse(self.validator.assert_id('some_string'))

    def test_validation(self):
        with mock.patch('jsonschema.validate') as mock_validate:
            self.validator.validate(self.FAKE_TESTS_RESULTS_JSON)
            mock_validate.assert_called_once_with(self.FAKE_TESTS_RESULTS_JSON,
                                                  self.validator.schema)

    def test_validation_fail(self):
        wrong_tests_result = json.dumps({
            'foo': 'bar'
        })
        self.assertRaises(jsonschema.ValidationError,
                          self.validator.validate,
                          wrong_tests_result)

    @mock.patch('pecan.request')
    def test_safe_load_json_body(self, mock_request):
        mock_request.body = self.FAKE_TESTS_RESULTS_JSON
        actual_result = validators.safe_load_json_body(self.validator)
        self.assertEqual(actual_result,
                         json.loads(self.FAKE_TESTS_RESULTS_JSON))

    @mock.patch('pecan.abort')
    @mock.patch('pecan.request')
    def test_safe_load_json_body_invalid_json(self, mock_request, mock_abort):
        mock_request.body = {}
        mock_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          validators.safe_load_json_body,
                          self.validator)

    @mock.patch('pecan.abort')
    @mock.patch('pecan.request')
    def test_safe_load_json_body_invalid_schema(self,
                                                mock_request,
                                                mock_abort):
        mock_request.body = json.dumps({'foo': 'bar'})
        mock_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          validators.safe_load_json_body,
                          self.validator)
