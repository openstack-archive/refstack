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

FAKE_PRODUCT = {
    'name': 'product name',
    'description': 'product description',
    'product_type': api_const.CLOUD,
}


class TestProductsEndpoint(api.FunctionalTest):
    """Test case for the 'products' API endpoint."""

    URL = '/v1/products/'

    def setUp(self):
        super(TestProductsEndpoint, self).setUp()
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
        """Test products endpoint with post request."""
        product = json.dumps(FAKE_PRODUCT)
        actual_response = self.post_json(self.URL, params=product)
        self.assertIn('id', actual_response)
        try:
            uuid.UUID(actual_response.get('id'), version=4)
        except ValueError:
            self.fail("actual_response doesn't contain new item id")

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_post_with_empty_object(self, mock_get_user):
        """Test products endpoint with empty product request."""
        results = json.dumps(dict())
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=results)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_post_with_invalid_schema(self, mock_get_user):
        """Test post request with invalid schema."""
        products = json.dumps({
            'foo': 'bar',
        })
        self.assertRaises(webtest.app.AppError,
                          self.post_json,
                          self.URL,
                          params=products)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_vendor_was_created(self, mock_get_user):
        """Test get_one request."""
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)

        get_response = self.get_json(self.URL + post_response.get('id'))
        vendor_id = get_response.get('organization_id')
        self.assertIsNotNone(vendor_id)

        # check vendor is present
        get_response = self.get_json('/v1/vendors/' + vendor_id)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_using_default_vendor(self, mock_get_user):
        """Test get_one request."""
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)

        get_response = self.get_json(self.URL + post_response.get('id'))
        vendor_id = get_response.get('organization_id')
        self.assertIsNotNone(vendor_id)

        # check vendor is present
        get_response = self.get_json('/v1/vendors/' + vendor_id)

        # create one more product
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_get_by_org(self, mock_get_user):
        """Test getting products of an organization."""
        org1 = db.add_organization({'name': 'test-vendor1'}, 'test-open-id')
        org2 = db.add_organization({'name': 'test-vendor2'}, 'test-open-id')
        prod_info = {'name': 'product1',
                     'description': 'product description',
                     'product_type': 1, 'type': 0,
                     'organization_id': org1['id'], 'public': True}
        prod1 = db.add_product(prod_info, 'test-open-id')
        prod_info['name'] = 'product2'
        prod_info['organization_id'] = org2['id']
        prod2 = db.add_product(prod_info, 'test-open-id')
        get_response = self.get_json(self.URL +
                                     '?organization_id=' + org1['id'])
        self.assertEqual(1, len(get_response['products']))
        self.assertEqual(prod1['id'], get_response['products'][0]['id'])

        get_response = self.get_json(self.URL +
                                     '?organization_id=' + org2['id'])
        self.assertEqual(1, len(get_response['products']))
        self.assertEqual(prod2['id'], get_response['products'][0]['id'])

        # Test that non-admin can't view non-public products of an org.
        db.update_product({'id': prod1['id'], 'public': False})
        mock_get_user.return_value = 'some-user'
        get_response = self.get_json(self.URL +
                                     '?organization_id=' + org1['id'])
        self.assertFalse(get_response['products'])

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_get_one(self, mock_get_user):
        """Test get_one request."""
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)

        get_response = self.get_json(self.URL + post_response.get('id'))
        # some of these fields are only exposed to the owner/foundation.
        self.assertIn('created_by_user', get_response)
        self.assertIn('properties', get_response)
        self.assertIn('created_at', get_response)
        self.assertIn('updated_at', get_response)
        self.assertEqual(FAKE_PRODUCT['name'],
                         get_response['name'])
        self.assertEqual(FAKE_PRODUCT['description'],
                         get_response['description'])
        self.assertEqual(api_const.PUBLIC_CLOUD,
                         get_response['type'])
        self.assertEqual(api_const.CLOUD,
                         get_response['product_type'])

        # reset auth and check return result for anonymous
        mock_get_user.return_value = None
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + post_response.get('id'))

        mock_get_user.return_value = 'foo-open-id'
        # Make product public.
        product_info = {'id': post_response.get('id'), 'public': 1}
        db.update_product(product_info)

        # Test when getting product info when not owner/foundation.
        get_response = self.get_json(self.URL + post_response.get('id'))
        self.assertNotIn('created_by_user', get_response)
        self.assertNotIn('created_at', get_response)
        self.assertNotIn('updated_at', get_response)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_delete(self, mock_get_user):
        """Test delete request."""
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)
        self.delete(self.URL + post_response.get('id'))

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_update(self, mock_get_user):
        """Test put(update) request."""
        product = json.dumps(FAKE_PRODUCT)
        post_response = self.post_json(self.URL, params=product)
        id = post_response.get('id')

        # check update of properties
        props = {'properties': {'fake01': 'value01'}}
        post_response = self.put_json(self.URL + id,
                                      params=json.dumps(props))
        get_response = self.get_json(self.URL + id)
        self.assertEqual(FAKE_PRODUCT['name'],
                         get_response['name'])
        self.assertEqual(FAKE_PRODUCT['description'],
                         get_response['description'])
        self.assertEqual(props['properties'],
                         json.loads(get_response['properties']))

        # check second update of properties
        props = {'properties': {'fake02': 'value03'}}
        post_response = self.put_json(self.URL + id,
                                      params=json.dumps(props))
        get_response = self.get_json(self.URL + id)
        self.assertEqual(props['properties'],
                         json.loads(get_response['properties']))

    def test_get_one_invalid_url(self):
        """Test get request with invalid url."""
        self.assertRaises(webtest.app.AppError,
                          self.get_json,
                          self.URL + 'fake_id')

    def test_get_with_empty_database(self):
        """Test get(list) request with no items in DB."""
        results = self.get_json(self.URL)
        self.assertEqual([], results['products'])


class TestProductVersionEndpoint(api.FunctionalTest):
    """Test case for the 'products/<product_id>/version' API endpoint."""

    def setUp(self):
        super(TestProductVersionEndpoint, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

        self.user_info = {
            'openid': 'test-open-id',
            'email': 'foo@bar.com',
            'fullname': 'Foo Bar'
        }
        db.user_save(self.user_info)

        patcher = mock.patch('refstack.api.utils.get_user_id')
        self.addCleanup(patcher.stop)
        self.mock_get_user = patcher.start()
        self.mock_get_user.return_value = 'test-open-id'

        product = json.dumps(FAKE_PRODUCT)
        response = self.post_json('/v1/products/', params=product)
        self.product_id = response['id']
        self.URL = '/v1/products/' + self.product_id + '/versions/'

    def test_get(self):
        """Test getting a list of versions."""
        response = self.get_json(self.URL)
        # Product created without version specified.
        self.assertIsNone(response[0]['version'])

        # Create a version
        post_response = self.post_json(self.URL,
                                       params=json.dumps({'version': '1.0'}))

        response = self.get_json(self.URL)
        self.assertEqual(2, len(response))
        self.assertEqual(post_response['version'], response[1]['version'])

    def test_get_one(self):
        """"Test get a specific version."""
        # Create a version
        post_response = self.post_json(self.URL,
                                       params=json.dumps({'version': '2.0'}))
        version_id = post_response['id']

        response = self.get_json(self.URL + version_id)
        self.assertEqual(post_response['version'], response['version'])

        # Test nonexistent version.
        self.assertRaises(webtest.app.AppError, self.get_json,
                          self.URL + 'sdsdsds')

    def test_post(self):
        """Test creating a product version."""
        version = {'cpid': '123', 'version': '5.0'}
        post_response = self.post_json(self.URL, params=json.dumps(version))

        get_response = self.get_json(self.URL + post_response['id'])
        self.assertEqual(version['cpid'], get_response['cpid'])
        self.assertEqual(version['version'], get_response['version'])
        self.assertEqual(self.product_id, get_response['product_id'])
        self.assertIn('id', get_response)

        # Test 'version' not in response body.
        response = self.post_json(self.URL, expect_errors=True,
                                  params=json.dumps({'cpid': '123'}))
        self.assertEqual(400, response.status_code)

    def test_put(self):
        """Test updating a product version."""
        post_response = self.post_json(self.URL,
                                       params=json.dumps({'version': '6.0'}))
        version_id = post_response['id']

        response = self.get_json(self.URL + version_id)
        self.assertIsNone(response['cpid'])

        props = {'cpid': '1233'}
        self.put_json(self.URL + version_id, params=json.dumps(props))

        response = self.get_json(self.URL + version_id)
        self.assertEqual('1233', response['cpid'])

    def test_delete(self):
        """Test deleting a product version."""
        post_response = self.post_json(self.URL,
                                       params=json.dumps({'version': '7.0'}))
        version_id = post_response['id']
        self.delete(self.URL + version_id)
        self.assertRaises(webtest.app.AppError, self.get_json,
                          self.URL + 'version_id')

        # Get the null version and ensure it can't be deleted.
        versions = self.get_json(self.URL)
        version_id = versions[0]['id']
        response = self.delete(self.URL + version_id, expect_errors=True)
        self.assertEqual(400, response.status_code)
