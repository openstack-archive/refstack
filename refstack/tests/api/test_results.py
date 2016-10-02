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

import mock
from oslo_config import fixture as config_fixture
import six
import webtest.app

from refstack.api import constants as api_const
from refstack.api import validators
from refstack import db
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

    @mock.patch('refstack.api.utils.check_owner')
    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_put(self, mock_user, mock_check_foundation, mock_check_owner):
        """Test results endpoint with put request."""
        results = json.dumps(FAKE_TESTS_RESULT)
        test_response = self.post_json(self.URL, params=results)
        test_id = test_response.get('test_id')
        url = self.URL + test_id

        user_info = {
            'openid': 'test-open-id',
            'email': 'foo@bar.com',
            'fullname': 'Foo Bar'
        }
        db.user_save(user_info)

        fake_product = {
            'name': 'product name',
            'description': 'product description',
            'product_type': api_const.CLOUD,
        }

        # Create a product
        product_response = self.post_json('/v1/products/',
                                          params=json.dumps(fake_product))
        # Create a product version
        version_url = '/v1/products/' + product_response['id'] + '/versions/'
        version_response = self.post_json(version_url,
                                          params=json.dumps({'version': '1'}))

        # Test Foundation admin can put.
        mock_check_foundation.return_value = True
        body = {'product_version_id': version_response['id']}
        self.put_json(url, params=json.dumps(body))
        get_response = self.get_json(url)
        self.assertEqual(version_response['id'],
                         get_response['product_version']['id'])

        # Test when product_version_id is None.
        body = {'product_version_id': None}
        self.put_json(url, params=json.dumps(body))
        get_response = self.get_json(url)
        self.assertIsNone(get_response['product_version'])

        # Test when test verification preconditions are not met.
        body = {'verification_status': api_const.TEST_VERIFIED}
        put_response = self.put_json(url, expect_errors=True,
                                     params=json.dumps(body))
        self.assertEqual(403, put_response.status_code)

        # Share the test run.
        db.save_test_meta_item(test_id, api_const.SHARED_TEST_RUN, True)
        put_response = self.put_json(url, expect_errors=True,
                                     params=json.dumps(body))
        self.assertEqual(403, put_response.status_code)

        # Now associate guideline and target program. Now we should be
        # able to mark a test verified.
        db.save_test_meta_item(test_id, 'target', 'platform')
        db.save_test_meta_item(test_id, 'guideline', '2016.01.json')
        put_response = self.put_json(url, params=json.dumps(body))
        self.assertEqual(api_const.TEST_VERIFIED,
                         put_response['verification_status'])

        # Unshare the test, and check that we can mark it not verified.
        db.delete_test_meta_item(test_id, api_const.SHARED_TEST_RUN)
        body = {'verification_status': api_const.TEST_NOT_VERIFIED}
        put_response = self.put_json(url, params=json.dumps(body))
        self.assertEqual(api_const.TEST_NOT_VERIFIED,
                         put_response['verification_status'])

        # Test when verification_status value is invalid.
        body = {'verification_status': 111}
        put_response = self.put_json(url, expect_errors=True,
                                     params=json.dumps(body))
        self.assertEqual(400, put_response.status_code)

        # Check test owner can put.
        mock_check_foundation.return_value = False
        mock_check_owner.return_value = True
        body = {'product_version_id': version_response['id']}
        self.put_json(url, params=json.dumps(body))
        get_response = self.get_json(url)
        self.assertEqual(version_response['id'],
                         get_response['product_version']['id'])

        # Test non-Foundation user can't change verification_status.
        body = {'verification_status': 1}
        put_response = self.put_json(url, expect_errors=True,
                                     params=json.dumps(body))
        self.assertEqual(403, put_response.status_code)

        # Test unauthorized put.
        mock_check_foundation.return_value = False
        mock_check_owner.return_value = False
        self.assertRaises(webtest.app.AppError,
                          self.put_json,
                          url,
                          params=json.dumps(body))

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

    @mock.patch('refstack.api.utils.get_user_id')
    def test_get_with_product_id(self, mock_get_user):
        user_info = {
            'openid': 'test-open-id',
            'email': 'foo@bar.com',
            'fullname': 'Foo Bar'
        }
        db.user_save(user_info)

        mock_get_user.return_value = 'test-open-id'

        fake_product = {
            'name': 'product name',
            'description': 'product description',
            'product_type': api_const.CLOUD,
        }

        product = json.dumps(fake_product)
        response = self.post_json('/v1/products/', params=product)
        product_id = response['id']

        # Create a version.
        version_url = '/v1/products/' + product_id + '/versions'
        version = {'cpid': '123', 'version': '6.0'}
        post_response = self.post_json(version_url, params=json.dumps(version))
        version_id = post_response['id']

        # Create a test and associate it to the product version and user.
        results = json.dumps(FAKE_TESTS_RESULT)
        post_response = self.post_json('/v1/results', params=results)
        test_id = post_response['test_id']
        test_info = {'id': test_id, 'product_version_id': version_id}
        db.update_test(test_info)
        db.save_test_meta_item(test_id, api_const.USER, 'test-open-id')

        url = self.URL + '?page=1&product_id=' + product_id

        # Test GET.
        response = self.get_json(url)
        self.assertEqual(1, len(response['results']))
        self.assertEqual(test_id, response['results'][0]['id'])

        # Test unauthorized.
        mock_get_user.return_value = 'test-foo-id'
        response = self.get_json(url, expect_errors=True)
        self.assertEqual(403, response.status_code)

        # Make product public.
        product_info = {'id': product_id, 'public': 1}
        db.update_product(product_info)

        # Test result is not shared yet, so no tests should return.
        response = self.get_json(url)
        self.assertFalse(response['results'])

        # Share the test run.
        db.save_test_meta_item(test_id, api_const.SHARED_TEST_RUN, 1)
        response = self.get_json(url)
        self.assertEqual(1, len(response['results']))
        self.assertEqual(test_id, response['results'][0]['id'])

    @mock.patch('refstack.api.utils.check_owner')
    def test_delete(self, mock_check_owner):
        results = json.dumps(FAKE_TESTS_RESULT)
        test_response = self.post_json(self.URL, params=results)
        test_id = test_response.get('test_id')
        url = self.URL + test_id

        mock_check_owner.return_value = True

        # Test can't delete verified test run.
        db.update_test({'id': test_id, 'verification_status': 1})
        resp = self.delete(url, expect_errors=True)
        self.assertEqual(403, resp.status_code)

        # Test can delete verified test run.
        db.update_test({'id': test_id, 'verification_status': 0})
        resp = self.delete(url, expect_errors=True)
        self.assertEqual(204, resp.status_code)
