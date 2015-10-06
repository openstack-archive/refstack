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

import httmock
from oslo_config import fixture as config_fixture
import six
import webtest.app

from refstack.api import validators
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

FAKE_JSON_WITH_EMPTY_RESULTS = {
    'cpid': 'foo',
    'duration_seconds': 20,
    'results': [
    ]
}


class TestResultsController(api.FunctionalTest):
    """Test case for ResultsController."""

    URL = '/v1/results/'

    def setUp(self):
        super(TestResultsController, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

    def test_post(self):
        """Test results endpoint with post request."""
        results = json.dumps(FAKE_TESTS_RESULT)
        actual_response = self.post_json(self.URL, params=results)
        self.assertIn('test_id', actual_response)
        try:
            uuid.UUID(actual_response.get('test_id'), version=4)
        except ValueError:
            self.fail("actual_response doesn't contain test_id")

    def test_post_with_empty_result(self):
        """Test results endpoint with empty test results request."""
        results = json.dumps(FAKE_JSON_WITH_EMPTY_RESULTS)
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=results)

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
        # CPID is only exposed to the owner.
        self.assertNotIn('cpid', get_response)
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

    def test_get_pagination(self):
        self.CONF.set_override('results_per_page',
                               2,
                               'api')

        responses = []
        for i in range(3):
            fake_results = {
                'cpid': six.text_type(i),
                'duration_seconds': i,
                'results': [
                    {'name': 'tempest.foo.bar'},
                    {'name': 'tempest.buzz'}
                ]
            }
            actual_response = self.post_json(self.URL,
                                             params=json.dumps(fake_results))
            responses.append(actual_response)

        page_one = self.get_json(self.URL)
        page_two = self.get_json('/v1/results?page=2')

        self.assertEqual(len(page_one['results']), 2)
        self.assertEqual(len(page_two['results']), 1)
        self.assertNotIn(page_two['results'][0], page_one)

        self.assertEqual(page_one['pagination']['current_page'], 1)
        self.assertEqual(page_one['pagination']['total_pages'], 2)

        self.assertEqual(page_two['pagination']['current_page'], 2)
        self.assertEqual(page_two['pagination']['total_pages'], 2)

        def test_get_with_not_existing_page(self):
            self.assertRaises(webtest.app.AppError,
                              self.get_json,
                              '/v1/results?page=2')

        def test_get_with_empty_database(self):
            results = self.get_json(self.URL)
            self.assertEqual(results, [])

        def test_get_with_cpid_filter(self):
            self.CONF.set_override('results_per_page',
                                   2,
                                   'api')

            responses = []
            for i in range(2):
                fake_results = {
                    'cpid': '12345',
                    'duration_seconds': i,
                    'results': [
                        {'name': 'tempest.foo'},
                        {'name': 'tempest.bar'}
                    ]
                }
                json_result = json.dumps(fake_results)
                actual_response = self.post_json(self.URL,
                                                 params=json_result)
                responses.append(actual_response)

            for i in range(3):
                fake_results = {
                    'cpid': '54321',
                    'duration_seconds': i,
                    'results': [
                        {'name': 'tempest.foo'},
                        {'name': 'tempest.bar'}
                    ]
                }

            results = self.get_json('/v1/results?page=1&cpid=12345')
            self.asserEqual(len(results), 2)

            for r in results:
                self.assertIn(r['test_id'], responses)

        def test_get_with_date_filters(self):
            self.CONF.set_override('results_per_page',
                                   10,
                                   'api')

            responses = []
            for i in range(5):
                fake_results = {
                    'cpid': '12345',
                    'duration_seconds': i,
                    'results': [
                        {'name': 'tempest.foo'},
                        {'name': 'tempest.bar'}
                    ]
                }
                json_result = json.dumps(fake_results)
                actual_response = self.post_json(self.URL,
                                                 params=json_result)
                responses.append(actual_response)

            all_results = self.get_json(self.URL)

            slice_results = all_results[1:3]

            url = 'v1/results?start_date=%(start)s&end_date=%(end)s' % {
                'start': slice_results[2]['created_at'],
                'end': slice_results[0]['created_at']
            }

            filtering_results = self.get_json(url)
            self.assertEqual(len(filtering_results), 3)
            for r in slice_results:
                self.assertEqual(r, filtering_results)


class TestCapabilitiesController(api.FunctionalTest):
    """Test case for CapabilitiesController."""

    URL = '/v1/capabilities/'

    def test_get_capability_list(self):
        @httmock.all_requests
        def github_api_mock(url, request):
            headers = {'content-type': 'application/json'}
            content = [{'name': '2015.03.json', 'type': 'file'},
                       {'name': '2015.next.json', 'type': 'file'},
                       {'name': '2015.03', 'type': 'dir'}]
            content = json.dumps(content)
            return httmock.response(200, content, headers, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            actual_response = self.get_json(self.URL)

        expected_response = ['2015.03.json']
        self.assertEqual(expected_response, actual_response)

    def test_get_capability_file(self):
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)
        url = self.URL + "2015.03"
        with httmock.HTTMock(github_mock):
            actual_response = self.get_json(url)

        expected_response = {'foo': 'bar'}
        self.assertEqual(expected_response, actual_response)
