#
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

"""Validators module."""

import binascii
import six
import uuid

import json
import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_ssh_public_key

from refstack.api import exceptions as api_exc

ext_format_checker = jsonschema.FormatChecker()


def is_uuid(inst):
    """Check that inst is a uuid_hex string."""
    try:
        uuid.UUID(hex=inst)
    except (TypeError, ValueError):
        return False
    return True


@jsonschema.FormatChecker.checks(ext_format_checker,
                                 format='uuid_hex',
                                 raises=(TypeError, ValueError))
def checker_uuid(inst):
    """Checker 'uuid_hex' format for jsonschema validator."""
    return is_uuid(inst)


class BaseValidator(object):
    """Base class for validators."""

    schema = {}

    def __init__(self):
        """Init."""
        jsonschema.Draft4Validator.check_schema(self.schema)
        self.validator = jsonschema.Draft4Validator(
            self.schema,
            format_checker=ext_format_checker
        )

    def validate(self, request):
        """Validate request."""
        try:
            body = json.loads(request.body)
        except (ValueError, TypeError) as e:
            raise api_exc.ValidationError('Malformed request', e)

        try:
            jsonschema.validate(body, self.schema)
        except jsonschema.ValidationError as e:
            raise api_exc.ValidationError(
                'Request doesn''t correspond to schema', e)

    def check_emptyness(self, body, keys):
        """Check that all values are not empty."""
        for key in keys:
            value = body[key]
            if isinstance(value, six.string_types):
                value = value.strip()
                if not value:
                    raise api_exc.ValidationError(key + ' should not be empty')
            elif value is None:
                raise api_exc.ValidationError(key + ' must be present')


class TestResultValidator(BaseValidator):
    """Validator for incoming test results."""

    schema = {
        'type': 'object',
        'properties': {
            'cpid': {
                'type': 'string'
            },
            'duration_seconds': {'type': 'integer'},
            'results': {
                'type': 'array',
                'items': [{
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'uuid': {
                            'type': 'string',
                            'format': 'uuid_hex'
                        }
                    }
                }]

            }
        },
        'required': ['cpid', 'duration_seconds', 'results'],
        'additionalProperties': False
    }

    def validate(self, request):
        """Validate uploaded test results."""
        super(TestResultValidator, self).validate(request)
        if request.headers.get('X-Signature') or \
                request.headers.get('X-Public-Key'):
            try:
                sign = binascii.a2b_hex(request.headers.get('X-Signature', ''))
            except (binascii.Error, TypeError) as e:
                raise api_exc.ValidationError('Malformed signature', e)

            try:
                key = load_ssh_public_key(
                    request.headers.get('X-Public-Key', ''),
                    backend=backends.default_backend()
                )
            except (binascii.Error, ValueError) as e:
                raise api_exc.ValidationError('Malformed public key', e)

            verifier = key.verifier(sign, padding.PKCS1v15(), hashes.SHA256())
            verifier.update(request.body.encode('utf-8'))
            try:
                verifier.verify()
            except InvalidSignature:
                raise api_exc.ValidationError('Signature verification failed')
        if self._is_empty_result(request):
            raise api_exc.ValidationError('Uploaded results must contain at '
                                          'least one passing test.')

    def _is_empty_result(self, request):
        """Check if the test results list is empty."""
        body = json.loads(request.body)
        if len(body['results']) != 0:
            return False
        return True

    @staticmethod
    def assert_id(_id):
        """Check that _id is a valid uuid_hex string."""
        return is_uuid(_id)


class PubkeyValidator(BaseValidator):
    """Validator for uploaded public pubkeys."""

    schema = {
        'type': 'object',
        'properties': {
            'raw_key': {'type': 'string'},
            'self_signature': {'type': 'string'}
        },
        'required': ['raw_key', 'self_signature'],
        'additionalProperties': False
    }

    def validate(self, request):
        """Validate uploaded test results."""
        super(PubkeyValidator, self).validate(request)
        body = json.loads(request.body)
        key_format = body['raw_key'].strip().split()[0]

        if key_format not in ('ssh-dss', 'ssh-rsa',
                              'pgp-sign-rsa', 'pgp-sign-dss'):
            raise api_exc.ValidationError('Public key has unsupported format')

        try:
            sign = binascii.a2b_hex(body['self_signature'])
        except (binascii.Error, TypeError) as e:
            raise api_exc.ValidationError('Malformed signature', e)

        try:
            key = load_ssh_public_key(body['raw_key'].encode('utf-8'),
                                      backend=backends.default_backend())
        except (binascii.Error, ValueError) as e:
            raise api_exc.ValidationError('Malformed public key', e)

        verifier = key.verifier(sign, padding.PKCS1v15(), hashes.SHA256())
        verifier.update('signature'.encode('utf-8'))
        try:
            verifier.verify()
        except InvalidSignature:
            raise api_exc.ValidationError('Signature verification failed')


class VendorValidator(BaseValidator):
    """Validator for adding new vendor."""

    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'description': {'type': 'string'},
        },
        'required': ['name'],
        'additionalProperties': False
    }

    def validate(self, request):
        """Validate uploaded vendor data."""
        super(VendorValidator, self).validate(request)
        body = json.loads(request.body)

        self.check_emptyness(body, ['name'])


class ProductValidator(BaseValidator):
    """Validate uploaded product data."""

    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'description': {'type': 'string'},
            'product_type': {'type': 'integer'},
            'organization_id': {'type': 'string', 'format': 'uuid_hex'},
            'version': {'type': 'string'}
        },
        'required': ['name', 'product_type'],
        'additionalProperties': False
    }

    def validate(self, request):
        """Validate uploaded test results."""
        super(ProductValidator, self).validate(request)
        body = json.loads(request.body)

        self.check_emptyness(body, ['name', 'product_type'])


class ProductVersionValidator(BaseValidator):
    """Validate adding product versions."""

    schema = {
        'type': 'object',
        'properties': {
            'version': {'type': 'string'},
            'cpid': {'type': 'string'}
        },
        'required': ['version'],
        'additionalProperties': False
    }

    def validate(self, request):
        """Validate product version data."""
        super(ProductVersionValidator, self).validate(request)
        body = json.loads(request.body)

        self.check_emptyness(body, ['version'])
