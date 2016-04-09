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
import webtest.app

from refstack.api import constants as api_const
from refstack import db
from refstack.tests import api

FAKE_VENDOR = {
    'name': 'vendor name',
    'description': 'vendor description',
}


class TestVendorsEndpoint(api.FunctionalTest):
    """Test case for the 'vendors' API endpoint."""

    URL = '/v1/vendors/'

    def setUp(self):
        super(TestVendorsEndpoint, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

        self.user_info = {
            'openid': 'test-open-id',
            'email': 'foo@bar.com',
            'fullname': 'Foo Bar'
        }
        db.user_save(self.user_info)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_post(self, mock_get_user):
        """Test vendors endpoint with post request."""
        vendor = json.dumps(FAKE_VENDOR)
        actual_response = self.post_json(self.URL, params=vendor)
        self.assertIn('id', actual_response)
        try:
            uuid.UUID(actual_response.get('id'), version=4)
        except ValueError:
            self.fail("actual_response doesn't contain new item id")

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_post_with_empty_object(self, mock_get_user):
        """Test vendors endpoint with empty vendor request."""
        results = json.dumps(dict())
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=results)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_post_with_invalid_schema(self, mock_get_user):
        """Test post request with invalid schema."""
        vendors = json.dumps({
            'foo': 'bar',
        })
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=vendors)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_get_one(self, mock_get_user):
        """Test get_one request."""
        vendor = json.dumps(FAKE_VENDOR)
        post_response = self.post_json(self.URL, params=vendor)

        get_response = self.get_json(self.URL + post_response.get('id'))
        # this fields are only exposed to the owner/foundation.
        self.assertIn('group_id', get_response)
        self.assertIn('created_by_user', get_response)
        self.assertIn('properties', get_response)
        self.assertIn('created_at', get_response)
        self.assertIn('updated_at', get_response)
        self.assertEqual(FAKE_VENDOR['name'],
                         get_response['name'])
        self.assertEqual(FAKE_VENDOR['description'],
                         get_response['description'])
        self.assertEqual(api_const.PRIVATE_VENDOR,
                         get_response['type'])

        # reset auth and check return result for anonymous
        mock_get_user.return_value = None
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + post_response.get('id'))

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_delete(self, mock_get_user):
        """Test delete request."""
        vendor = json.dumps(FAKE_VENDOR)
        post_response = self.post_json(self.URL, params=vendor)
        self.delete(self.URL + post_response.get('id'))

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_action(self, mock_get_user):
        """Test action/register request."""
        vendor = json.dumps(FAKE_VENDOR)
        post_response = self.post_json(self.URL, params=vendor)
        vendor_id = post_response.get('id')
        self.post_json(self.URL + vendor_id + '/action',
                       params=json.dumps({'register': None}))
        get_response = self.get_json(self.URL + vendor_id)
        self.assertEqual(api_const.PENDING_VENDOR,
                         get_response['type'])

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_update(self, mock_get_user):
        """Test put(update) request."""
        vendor = json.dumps(FAKE_VENDOR)
        post_response = self.post_json(self.URL, params=vendor)
        vendor_id = post_response.get('id')

        # check update of properties
        props = {'properties': {'fake01': 'value01'}}
        post_response = self.put_json(self.URL + vendor_id,
                                      params=json.dumps(props))
        get_response = self.get_json(self.URL + vendor_id)
        self.assertEqual(FAKE_VENDOR['name'],
                         get_response['name'])
        self.assertEqual(FAKE_VENDOR['description'],
                         get_response['description'])
        self.assertEqual(props['properties'],
                         json.loads(get_response['properties']))

        # check second update of properties
        props = {'properties': {'fake02': 'value03'}}
        post_response = self.put_json(self.URL + vendor_id,
                                      params=json.dumps(props))
        get_response = self.get_json(self.URL + vendor_id)
        self.assertEqual(props['properties'],
                         json.loads(get_response['properties']))

    def test_get_one_invalid_url(self):
        """Test get request with invalid url."""
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + 'fake_url')

    def test_get_with_empty_database(self):
        """Test get(list) request with no items in DB."""
        results = self.get_json(self.URL)
        self.assertEqual([], results['vendors'])
