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
