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

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import jsonschema
import mock
from oslotest import base
import six

from refstack.common import validators


class ValidatorsTestCase(base.BaseTestCase):
    """Test case for validator's helpers."""

    def test_str_validation_error(self):
        err = validators.ValidationError(
            'Something went wrong!',
            AttributeError("'NoneType' object has no attribute 'a'")
        )
        self.assertEqual(err.title, 'Something went wrong!')
        self.assertEqual("%s(%s: %s)" % (
            'Something went wrong!',
            'AttributeError',
            "'NoneType' object has no attribute 'a'"
        ), str(err))
        err = validators.ValidationError(
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

    FAKE_TESTS_RESULTS_JSON = {
        'cpid': 'foo',
        'duration_seconds': 10,
        'results': [
            {'name': 'tempest.some.test'},
            {'name': 'tempest.test', 'uid': '12345678'}
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
            request.body = json.dumps(self.FAKE_TESTS_RESULTS_JSON)
            request.headers = {}
            self.validator.validate(request)
            mock_validate.assert_called_once_with(self.FAKE_TESTS_RESULTS_JSON,
                                                  self.validator.schema)

    @mock.patch('jsonschema.validate')
    def test_validation_with_signature(self, mock_validate):
        if six.PY3:
            self.skip('https://github.com/dlitz/pycrypto/issues/99')
        request = mock.Mock()
        request.body = json.dumps(self.FAKE_TESTS_RESULTS_JSON)
        data_hash = SHA256.new()
        data_hash.update(request.body.encode('utf-8'))
        key = RSA.generate(4096)
        signer = PKCS1_v1_5.new(key)
        sign = signer.sign(data_hash)
        request.headers = {
            'X-Signature': binascii.b2a_hex(sign),
            'X-Public-Key': key.publickey().exportKey('OpenSSH')
        }
        self.validator.validate(request)
        mock_validate.assert_called_once_with(self.FAKE_TESTS_RESULTS_JSON,
                                              self.validator.schema)

    def test_validation_fail_no_json(self):
        wrong_request = mock.Mock()
        wrong_request.body = 'foo'
        self.assertRaises(validators.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except validators.ValidationError as e:
            self.assertIsInstance(e.exc, ValueError)

    def test_validation_fail(self):
        wrong_request = mock.Mock()
        wrong_request.body = json.dumps({
            'foo': 'bar'
        })
        self.assertRaises(validators.ValidationError,
                          self.validator.validate,
                          wrong_request)
        try:
            self.validator.validate(wrong_request)
        except validators.ValidationError as e:
            self.assertIsInstance(e.exc, jsonschema.ValidationError)

    @mock.patch('jsonschema.validate')
    def test_validation_with_broken_signature(self, mock_validate):
        if six.PY3:
            self.skip('https://github.com/dlitz/pycrypto/issues/99')

        request = mock.Mock()
        request.body = json.dumps(self.FAKE_TESTS_RESULTS_JSON)
        key = RSA.generate(2048)
        request.headers = {
            'X-Signature': binascii.b2a_hex('fake_sign'.encode('utf-8')),
            'X-Public-Key': key.publickey().exportKey('OpenSSH')
        }
        self.assertRaises(validators.ValidationError,
                          self.validator.validate,
                          request)
        request.headers = {
            'X-Signature': binascii.b2a_hex('fake_sign'.encode('utf-8')),
            'X-Public-Key': key.publickey().exportKey('OpenSSH')
        }
        try:
            self.validator.validate(request)
        except validators.ValidationError as e:
            self.assertEqual(e.title,
                             'Signature verification failed')

        request.headers = {
            'X-Signature': 'z-z-z-z!!!',
            'X-Public-Key': key.publickey().exportKey('OpenSSH')
        }
        try:
            self.validator.validate(request)
        except validators.ValidationError as e:
            self.assertIsInstance(e.exc, TypeError)

        request.headers = {
            'X-Signature': binascii.b2a_hex('fake_sign'),
            'X-Public-Key': 'H--0'
        }
        try:
            self.validator.validate(request)
        except validators.ValidationError as e:
            self.assertIsInstance(e.exc, ValueError)
