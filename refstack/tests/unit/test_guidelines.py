# Copyright (c) 2016 IBM, Inc.
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
import mock
from oslotest import base
import requests

from refstack.api import guidelines


class GuidelinesTestCase(base.BaseTestCase):

    def setUp(self):
        super(GuidelinesTestCase, self).setUp()
        self.guidelines = guidelines.Guidelines()

    def test_guidelines_list(self):
        @httmock.all_requests
        def github_api_mock(url, request):
            headers = {'content-type': 'application/json'}
            content = [{'name': '2015.03.json', 'type': 'file'},
                       {'name': '2015.next.json', 'type': 'file'},
                       {'name': '2015.03', 'type': 'dir'}]
            content = json.dumps(content)
            return httmock.response(200, content, headers, None, 5, request)
        with httmock.HTTMock(github_api_mock):
            result = self.guidelines.get_guideline_list()
        self.assertEqual(['2015.03.json'], result)

    def test_get_guidelines_list_error_code(self):
        """Test when the HTTP status code isn't a 200 OK."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            result = self.guidelines.get_guideline_list()
        self.assertIsNone(result)

    @mock.patch('requests.get')
    def test_get_guidelines_exception(self, mock_requests_get):
        """Test when the GET request raises an exception."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        result = self.guidelines.get_guideline_list()
        self.assertIsNone(result)

    def test_get_capability_file(self):
        """Test when getting a specific guideline file"""
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)

        with httmock.HTTMock(github_mock):
            result = self.guidelines.get_guideline_contents('2010.03.json')
        self.assertEqual({'foo': 'bar'}, result)

    def test_get_capability_file_error_code(self):
        """Test when the HTTP status code isn't a 200 OK."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            result = self.guidelines.get_guideline_contents('2010.03.json')
        self.assertIsNone(result)

    @mock.patch('requests.get')
    def test_get_capability_file_exception(self, mock_requests_get):
        """Test when the GET request raises an exception."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        result = self.guidelines.get_guideline_contents('2010.03.json')
        self.assertIsNone(result)

    def test_get_target_capabilities(self):
        """Test getting relevant capabilities."""
        json = {
            'platform': {'required': ['compute', 'object']},
            'schema': '1.4',
            'components': {
                'compute': {
                    'required': ['cap_id_1'],
                    'advisory': [],
                    'deprecated': [],
                    'removed': []
                },
                'object': {
                    'required': ['cap_id_2'],
                    'advisory': ['cap_id_3'],
                    'deprecated': [],
                    'removed': []
                }
            }
        }

        # Test platform capabilities
        caps = self.guidelines.get_target_capabilities(json)
        expected = sorted(['cap_id_1', 'cap_id_2', 'cap_id_3'])
        self.assertEqual(expected, sorted(caps))

        caps = self.guidelines.get_target_capabilities(json,
                                                       types=['required'],
                                                       target='object')
        expected = ['cap_id_2']
        self.assertEqual(expected, caps)

    def test_get_test_list(self):
        """Test when getting the guideline test list."""

        # Schema version 1.4
        json = {
            'schema': '1.4',
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
        tests = self.guidelines.get_test_list(json, ['cap-1'])
        expected = ['test_1[id-1234]', 'test_2[id-5678]',
                    'test_2_1[id-5678]', 'test_3[id-1111]']
        self.assertEqual(expected, tests)

        tests = self.guidelines.get_test_list(json, ['cap-1'],
                                              alias=False, show_flagged=False)
        expected = ['test_1[id-1234]', 'test_2[id-5678]']
        self.assertEqual(expected, tests)

        # Schema version 1.2
        json = {
            'schema': '1.2',
            'capabilities': {
                'cap-1': {
                    'tests': ['test_1', 'test_2']
                },
                'cap-2': {
                    'tests': ['test_3']
                }
            }
        }
        tests = self.guidelines.get_test_list(json, ['cap-2'])
        self.assertEqual(['test_3'], tests)
