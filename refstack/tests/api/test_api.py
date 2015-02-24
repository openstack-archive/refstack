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

"""Functional tests for refstack's API."""

import json
import uuid

import six
import webtest.app

from refstack.common import validators
from refstack.tests import api

FAKE_TESTS_RESULT = {
    'cpid': 'foo',
    'duration_seconds': 10,
    'results': [
        {'name': 'tempest.foo.bar'},
        {'name': 'tempest.buzz',
         'uid': '42'}
    ]
}


class TestRootController(api.FunctionalTest):
    """Test case for RootController."""

    URL = '/'

    def test_root_controller(self):
        """Test request to root."""
        actual_response = self.get_json(self.URL)
        expected_response = {'Root': 'OK'}
        self.assertEqual(expected_response, actual_response)


class TestResultsController(api.FunctionalTest):
    """Test case for ResultsController."""

    URL = '/v1/results/'

    def test_post(self):
        """Test results endpoint with post request."""
        results = json.dumps(FAKE_TESTS_RESULT)
        actual_response = self.post_json(self.URL, params=results)
        self.assertIn('test_id', actual_response)
        try:
            uuid.UUID(actual_response.get('test_id'), version=4)
        except ValueError:
            self.fail("actual_response doesn't contain test_id")

    def test_post_with_invalid_schema(self):
        """Test post request with invalid schema."""
        results = json.dumps({
            'foo': 'bar',
            'duration_seconds': 999,
        })
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=results)

    def test_get_one(self):
        """Test get request."""
        results = json.dumps(FAKE_TESTS_RESULT)
        post_response = self.post_json(self.URL, params=results)
        get_response = self.get_json(self.URL + post_response.get('test_id'))
        self.assertEqual(FAKE_TESTS_RESULT['cpid'],
                         get_response['cpid'])
        self.assertEqual(FAKE_TESTS_RESULT['duration_seconds'],
                         get_response['duration_seconds'])
        for test in FAKE_TESTS_RESULT['results']:
            self.assertIn(test['name'], get_response['results'])

    def test_get_one_with_nonexistent_uuid(self):
        """Test get request with nonexistent uuid."""
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + six.text_type(uuid.uuid4()))

    def test_get_one_schema(self):
        """Test get request for getting JSON schema."""
        validator = validators.TestResultValidator()
        expected_schema = validator.schema
        actual_schema = self.get_json(self.URL + 'schema')
        self.assertEqual(actual_schema, expected_schema)

    def test_get_one_invalid_url(self):
        """Test get request with invalid url."""
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + 'fake_url')
