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
            content = [{'name': '2015.03.json',
                        'path': '2015.03.json',
                        'type': 'file'},
                       {'name': '2015.next.json',
                        'path': '2015.next.json',
                        'type': 'file'},
                       {'name': '2015.03',
                        'path': '2015.03',
                        'type': 'dir'},
                       {'name': 'test.2018.02.json',
                        'path': 'add-ons/test.2018.02.json',
                        'type': 'file'},
                       {'name': 'test.next.json',
                        'path': 'add-ons/test.next.json',
                        'type': 'file'}]
            content = json.dumps(content)
            return httmock.response(200, content, headers, None, 5, request)
        with httmock.HTTMock(github_api_mock):
            result = self.guidelines.get_guideline_list()
        expected_keys = ['powered', u'test']
        expected_powered = [
            {'name': u'2015.03.json',
             'file': u'2015.03.json'},
            {'name': u'2015.next.json',
             'file': u'2015.next.json'}
        ]
        expected_test_addons = [
            {'name': u'2018.02.json',
             'file': u'test.2018.02.json'},
            {'name': u'next.json',
             'file': u'test.next.json'}
        ]

        self.assertIn('powered', expected_keys)
        self.assertIn(u'test', expected_keys)
        self.assertEqual(expected_powered,
                         result['powered'])
        self.assertEqual(expected_test_addons,
                         result[u'test'])

    def test_get_guidelines_list_error_code(self):
        """Test when the HTTP status code isn't a 200 OK."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            result = self.guidelines.get_guideline_list()
        self.assertEqual(result, {'powered': []})

    @mock.patch('requests.get')
    def test_get_guidelines_exception(self, mock_requests_get):
        """Test when the GET request raises an exception."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        result = self.guidelines.get_guideline_list()
        self.assertEqual(result, {'powered': []})

    def test_get_capability_file(self):
        """Test when getting a specific guideline file."""
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)

        with httmock.HTTMock(github_mock):
            gl_file_name = 'dns.2018.02.json'
            result = self.guidelines.get_guideline_contents(gl_file_name)
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

        # Schema version 2.0
        json = {
            'metadata': {
                'id': '2017.08',
                'schema': '2.0',
                'scoring': {},
                'os_trademark_approval': {
                    'target_approval': '2017.08',
                    'replaces': '2017.01',
                    'releases': ['newton', 'ocata', 'pike'],
                    'status': 'approved'
                }
            },
            'platforms': {
                'OpenStack Powered Platform': {
                    'description': 'foo platform',
                    'components': [
                        {'name': 'os_powered_compute'},
                        {'name': 'os_powered_storage'}
                    ]
                },
                'OpenStack Powered Storage': {
                    'description': 'foo storage',
                    'components': [
                        {'name': 'os_powered_storage'}
                    ]
                },
            },
            'components': {
                'os_powered_compute': {
                    'capabilities': {
                        'required': ['cap_id_1'],
                        'advisory': ['cap_id_2'],
                        'deprecated': ['cap_id_3'],
                        'removed': []
                    }
                },
                'os_powered_storage': {
                    'capabilities': {
                        'required': ['cap_id_5'],
                        'advisory': ['cap_id_6'],
                        'deprecated': [],
                        'removed': []
                    }
                }
            }
        }

        caps = self.guidelines.get_target_capabilities(json)
        expected = sorted(['cap_id_1', 'cap_id_2', 'cap_id_3',
                           'cap_id_5', 'cap_id_6'])
        self.assertEqual(expected, sorted(caps))

        caps = self.guidelines.get_target_capabilities(json,
                                                       types=['required'],
                                                       target='object')
        expected = ['cap_id_5']
        self.assertEqual(expected, caps)

        # Schema version 1.4
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

        # Schema version 2.0
        json = {
            'metadata': {
                'schema': '2.0',
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

        tests = self.guidelines.get_test_list(json, ['cap-1'])
        expected = ['test_1[id-1234]', 'test_2[id-5678]',
                    'test_2_1[id-5678]', 'test_3[id-1111]']
        self.assertEqual(expected, tests)

        tests = self.guidelines.get_test_list(json, ['cap-1'],
                                              alias=False, show_flagged=False)
        expected = ['test_1[id-1234]', 'test_2[id-5678]']
        self.assertEqual(expected, tests)

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
