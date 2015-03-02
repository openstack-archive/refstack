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

""" Validators module
"""

import uuid

import json
import jsonschema
import pecan

ext_format_checker = jsonschema.FormatChecker()


def is_uuid(inst):
    """ Check that inst is a uuid_hex string. """
    try:
        uuid.UUID(hex=inst)
    except (TypeError, ValueError):
        return False
    return True


@jsonschema.FormatChecker.checks(ext_format_checker,
                                 format='uuid_hex',
                                 raises=(TypeError, ValueError))
def checker_uuid(inst):
    """Checker 'uuid_hex' format for jsonschema validator"""
    return is_uuid(inst)


class Validator(object):

    """Base class for validators"""

    def validate(self, json_data):
        """
        :param json_data: data for validation
        """
        jsonschema.validate(json_data, self.schema)


class TestResultValidator(Validator):

    """Validator for incoming test results."""

    def __init__(self):

        self.schema = {
            'type': 'object',
            'properties': {
                'cpid': {
                    'type': 'string'
                },
                'duration_seconds': {'type': 'integer'},
                'results': {
                    "type": "array",
                    "items": [{
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'uid': {
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
        jsonschema.Draft4Validator.check_schema(self.schema)
        self.validator = jsonschema.Draft4Validator(
            self.schema,
            format_checker=ext_format_checker
        )

    @staticmethod
    def assert_id(_id):
        """ Check that _id is a valid uuid_hex string. """
        return is_uuid(_id)


def safe_load_json_body(validator):
    """
    Helper for load validated request body
    :param validator: instance of Validator class
    :return validated body
    :raise ValueError, jsonschema.ValidationError
    """
    body = ''
    try:
        body = json.loads(pecan.request.body)
    except (ValueError, TypeError) as e:
        pecan.abort(400, detail=e.message)

    try:
        validator.validate(body)
    except jsonschema.ValidationError as e:
        pecan.abort(400,
                    detail=e.message,
                    title='Malformed json data, '
                          'see %s/schema' % pecan.request.path_url)

    return body
