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

import json
import uuid

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


class TestResultsEndpoint(api.FunctionalTest):
    """Test case for the 'results' API endpoint."""

    URL = '/v1/results/'

    def setUp(self):
        super(TestResultsEndpoint, self).setUp()
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
        self.assertEqual([], results['results'])

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
        self.assertEqual(len(results), 2)
        response_test_ids = [test['test_id'] for test in responses[0:2]]
        for r in results['results']:
            self.assertIn(r['id'], response_test_ids)

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

        slice_results = all_results['results'][1:4]

        url = '/v1/results?start_date=%(start)s&end_date=%(end)s' % {
            'start': slice_results[2]['created_at'],
            'end': slice_results[0]['created_at']
        }

        filtering_results = self.get_json(url)
        for r in slice_results:
            self.assertIn(r, filtering_results['results'])

        url = '/v1/results?end_date=1000-01-01 12:00:00'
        filtering_results = self.get_json(url)
        self.assertEqual([], filtering_results['results'])
