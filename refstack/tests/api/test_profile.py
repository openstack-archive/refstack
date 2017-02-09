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

import binascii
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import mock
import webtest.app

from refstack.tests import api
from refstack import db


class TestProfileEndpoint(api.FunctionalTest):
    """Test case for the 'profile' API endpoint."""

    URL = '/v1/profile/'

    def setUp(self):
        super(TestProfileEndpoint, self).setUp()
        self.user_info = {
            'openid': 'test-open-id',
            'email': 'foo@bar.com',
            'fullname': 'Foo Bar'
        }
        db.user_save(self.user_info)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_get(self, mock_get_user):
        response = self.get_json(self.URL)
        self.user_info['is_admin'] = False
        self.assertEqual(self.user_info, response)

    @mock.patch('refstack.api.utils.get_user_id', return_value='test-open-id')
    def test_pubkeys(self, mock_get_user):
        """Test '/v1/profile/pubkeys' API endpoint."""
        url = self.URL + 'pubkeys'
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend()
        )
        signer = key.signer(padding.PKCS1v15(), hashes.SHA256())
        signer.update('signature'.encode('utf-8'))
        sign = signer.finalize()
        pubkey = key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        body = {'raw_key': pubkey,
                'self_signature': binascii.b2a_hex(sign)}
        json_params = json.dumps(body)

        # POST endpoint
        pubkey_id = self.post_json(url, params=json_params)

        # GET endpoint
        user_pubkeys = self.get_json(url)
        self.assertEqual(1, len(user_pubkeys))
        self.assertEqual(pubkey.split()[1], user_pubkeys[0]['pubkey'])
        self.assertEqual('ssh-rsa', user_pubkeys[0]['format'])
        self.assertEqual(pubkey_id, user_pubkeys[0]['id'])

        delete_url = '{}/{}'.format(url, pubkey_id)
        # DELETE endpoint
        response = self.delete(delete_url)
        self.assertEqual(204, response.status_code)

        user_pubkeys = self.get_json(url)
        self.assertEqual(0, len(user_pubkeys))

        # DELETE endpoint - nonexistent pubkey
        self.assertRaises(webtest.app.AppError, self.delete, delete_url)
