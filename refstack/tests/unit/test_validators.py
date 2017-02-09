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
import binascii
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

import jsonschema
import mock
from oslotest import base

from refstack.api import exceptions as api_exc
from refstack.api import validators


class ValidatorsTestCase(base.BaseTestCase):
    """Test case for validator's helpers."""

    def test_str_validation_error(self):
        err = api_exc.ValidationError(
            'Something went wrong!',
            AttributeError("'NoneType' object has no attribute 'a'")
        )
        self.assertEqual(err.title, 'Something went wrong!')
        self.assertEqual("%s(%s: %s)" % (
            'Something went wrong!',
            'AttributeError',
            "'NoneType' object has no attribute 'a'"
        ), str(err))
        err = api_exc.ValidationError(
            'Something went wrong again!'
        )
        self.assertEqual('Something went wrong again!', str(err))

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
    """Test case for TestResultValidator."""

    FAKE_JSON = {
        'cpid': 'foo',
        'duration_seconds': 10,
        'results': [
            {'name': 'tempest.some.test'},
            {'name': 'tempest.test', 'uid': '12345678'}
        ]
    }

    FAKE_JSON_WITH_EMPTY_RESULTS = {
        'cpid': 'foo',
        'duration_seconds': 20,
        'results': [
        ]
    }

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
            request = mock.Mock()
            request.body = json.dumps(self.FAKE_JSON)
            request.headers = {}
            self.validator.validate(request)
            mock_validate.assert_called_once_with(self.FAKE_JSON,
                                                  self.validator.schema)

    def test_validation_with_signature(self):
        request = mock.Mock()
        request.body = json.dumps(self.FAKE_JSON)

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
            backend=default_backend()
        )
        signer = key.signer(padding.PKCS1v15(), hashes.SHA256())
        signer.update(request.body.encode('utf-8'))
        sign = signer.finalize()
        pubkey = key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        request.headers = {
            'X-Signature': binascii.b2a_hex(sign),
            'X-Public-Key': pubkey
        }
        self.validator.validate(request)

    def test_validation_fail_no_json(self):
        wrong_request = mock.Mock()
        wrong_request.body = 'foo'
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except api_exc.ValidationError as e:
            self.assertIsInstance(e.exc, ValueError)

    def test_validation_fail(self):
        wrong_request = mock.Mock()
        wrong_request.body = json.dumps({
            'foo': 'bar'
        })
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except api_exc.ValidationError as e:
            self.assertIsInstance(e.exc, jsonschema.ValidationError)

    def test_validation_fail_with_empty_result(self):
        wrong_request = mock.Mock()
        wrong_request.body = json.dumps(self.FAKE_JSON_WITH_EMPTY_RESULTS)
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          wrong_request)

    @mock.patch('jsonschema.validate')
    def test_validation_with_broken_signature(self, mock_validate):

        request = mock.Mock()
        request.body = json.dumps(self.FAKE_JSON)
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        pubkey = key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        request.headers = {
            'X-Signature': binascii.b2a_hex(b'fake_sign'),
            'X-Public-Key': pubkey
        }
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          request)
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title,
                             'Signature verification failed')

        request.headers = {
            'X-Signature': 'z-z-z-z!!!',
            'X-Public-Key': pubkey
        }
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title, 'Malformed signature')

        request.headers = {
            'X-Signature': binascii.b2a_hex(b'fake_sign'),
            'X-Public-Key': b'H--0'
        }
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertIsInstance(e.exc, ValueError)


class PubkeyValidatorTestCase(base.BaseTestCase):
    """Test case for TestResultValidator."""

    FAKE_JSON = {
        'raw_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC4GAwIjFN6mkN09Vfc8h'
                   'VCnbztex/kjVdPlGraBLR+M9VoehOMJgLawpn2f+rM7NjDDgIwvj0kHVMZ'
                   'cBk5MZ1eQg3ACtP2EBw0SLLZ9uMSuHoDTf8oHVgNlNrHL3sc/QYJYfSqRh'
                   'FS2JvIVNnC2iG8jwnxUBI9rBspYU8AkrrczQ== Don\'t_Panic.',
        'self_signature': '9d6c4c74b4ec47bb4db8f288a502d2d2f686e7228d387377b8'
                          'c89ee67345ad04f8e518e0a627afe07217defbbd8acdd6dd88'
                          '74104e631731a1fb4dab1a34e06a0680f11337d1fae0b7a9ad'
                          '5942e0aacd2245c4cf7a78a96c4800eb4f6d8c363822aaaf43'
                          'aa3a648ddee84f3ea0b91e2e977ca19df72ad80226c12b1221'
                          'c2fb61'
    }

    def setUp(self):
        super(PubkeyValidatorTestCase, self).setUp()
        self.validator = validators.PubkeyValidator()

    def test_validation(self):
        request = mock.Mock()
        request.body = json.dumps(self.FAKE_JSON)
        self.validator.validate(request)

    def test_validation_fail_no_json(self):
        wrong_request = mock.Mock()
        wrong_request.body = 'foo'
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except api_exc.ValidationError as e:
            self.assertIsInstance(e.exc, ValueError)

    def test_validation_fail(self):
        wrong_request = mock.Mock()
        wrong_request.body = json.dumps({
            'foo': 'bar'
        })
        self.assertRaises(api_exc.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except api_exc.ValidationError as e:
            self.assertIsInstance(e.exc, jsonschema.ValidationError)

    @mock.patch('jsonschema.validate')
    def test_validation_with_broken_signature(self, mock_validate):
        body = self.FAKE_JSON.copy()
        body['self_signature'] = 'deadbeef'

        request = mock.Mock()
        request.body = json.dumps(body)
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title,
                             'Signature verification failed')

        body = {
            'raw_key': 'fake key comment',
            'self_signature': 'deadbeef'
        }
        request = mock.Mock()
        request.body = json.dumps(body)
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title,
                             'Public key has unsupported format')

        body = {
            'raw_key': 'ssh-rsa key comment',
            'self_signature': 'deadbeef?'
        }
        request = mock.Mock()
        request.body = json.dumps(body)
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title,
                             'Malformed signature')

        body = {
            'raw_key': 'ssh-rsa key comment',
            'self_signature': 'deadbeef'
        }
        request = mock.Mock()
        request.body = json.dumps(body)
        try:
            self.validator.validate(request)
        except api_exc.ValidationError as e:
            self.assertEqual(e.title,
                             'Malformed public key')
