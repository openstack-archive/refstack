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

import httmock

from refstack.tests import api


class TestGuidelinesEndpoint(api.FunctionalTest):
    """Test case for the 'guidelines' API endpoint."""

    URL = '/v1/guidelines/'

    def test_get_guideline_list(self):
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

    def test_get_guideline_file(self):
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)
        url = self.URL + "2015.03"
        with httmock.HTTMock(github_mock):
            actual_response = self.get_json(url)

        expected_response = {'foo': 'bar'}
        self.assertEqual(expected_response, actual_response)

    def test_get_guideline_test_list(self):
        @httmock.all_requests
        def github_mock(url, request):
            content = {
                'schema': '1.4',
                'platform': {'required': ['compute', 'object']},
                'components': {
                    'compute': {
                        'required': ['cap-1'],
                        'advisory': [],
                        'deprecated': [],
                        'removed': []
                    },
                    'object': {
                        'required': ['cap-2'],
                        'advisory': ['cap-3'],
                        'deprecated': [],
                        'removed': []
                    }
                },
                'capabilities': {
                    'cap-1': {
                        'tests': {
                            'test_1': {'idempotent_id': 'id-1234'},
                            'test_2': {'idempotent_id': 'id-5678',
                                       'aliases': ['test_2_1']},
                            'test_3': {'idempotent_id': 'id-1111',
                                       'flagged': {'reason': 'foo'}}
                        }
                    },
                    'cap-2': {
                        'tests': {
                            'test_4': {'idempotent_id': 'id-1233'}
                        }
                    }
                }
            }
            return httmock.response(200, content, None, None, 5, request)
        url = self.URL + "2016.03/tests"
        with httmock.HTTMock(github_mock):
            actual_response = self.get_json(url, expect_errors=True)

        expected_list = ['test_1[id-1234]', 'test_2[id-5678]',
                         'test_2_1[id-5678]', 'test_3[id-1111]',
                         'test_4[id-1233]']
        expected_response = '\n'.join(expected_list)
        self.assertEqual(expected_response, actual_response.text)
