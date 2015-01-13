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

"""Base classes for API tests.
"""
from unittest import TestCase
from pecan import set_config
from pecan.testing import load_test_app


class FunctionalTest(TestCase):
    """
    Used for functional tests where you need to test your
    literal application and its integration with the framework.
    """

    def setUp(self):
        self.config = {
            'app': {
                'root': 'refstack.api.controllers.root.RootController',
                'modules': ['refstack.api'],
                'static_root': '%(confdir)s/public',
                'template_path': '%(confdir)s/${package}/templates',
            }
        }
        self.app = load_test_app(self.config)

    def tearDown(self):
        set_config({}, overwrite=True)

    def get_json(self, url, headers=None, extra_environ=None,
                 status=None, expect_errors=False, **params):
        """Sends HTTP GET request.

        :param url: url path to target service
        :param headers: a dictionary of extra headers to send
        :param extra_environ: a dictionary of environmental variables that
                              should be added to the request
        :param status: integer or string of the HTTP status code you expect
                       in response (if not 200 or 3xx). You can also use a
                       wildcard, like '3*' or '*'
        :param expect_errors: boolean value, if this is False, then if
                              anything is written to environ wsgi.errors it
                              will be an error. If it is True, then
                              non-200/3xx responses are also okay
        :param params: a query string, or a dictionary that will be encoded
                       into a query string. You may also include a URL query
                       string on the url

        """
        response = self.app.get(url,
                                headers=headers,
                                extra_environ=extra_environ,
                                status=status,
                                expect_errors=expect_errors,
                                params=params)

        if not expect_errors:
            response = response.json
        return response
