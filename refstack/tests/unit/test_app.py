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

"""Tests for API's utility"""

import json

import mock
from oslo_config import fixture as config_fixture
from oslotest import base
import webob

from refstack.api import app
from refstack.common import validators


def get_response_kwargs(response_mock):
    _, kwargs = response_mock.call_args
    if kwargs['body']:
        kwargs['body'] = json.loads(kwargs.get('body', ''))
    return kwargs


class JSONErrorHookTestCase(base.BaseTestCase):

    def setUp(self):
        super(JSONErrorHookTestCase, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

    def _on_error(self, response, exc, expected_status_code, expected_body):
        response.return_value = 'fake_value'
        hook = app.JSONErrorHook()
        result = hook.on_error(mock.Mock(), exc)
        self.assertEqual(result, 'fake_value')
        self.assertEqual(
            dict(body=expected_body,
                 status=expected_status_code,
                 content_type='application/json'),
            get_response_kwargs(response)
        )

    @mock.patch.object(webob, 'Response')
    def test_on_error_with_webob_instance(self, response):
        self.CONF.set_override('app_dev_mode', False, 'api')
        exc = mock.Mock(spec=webob.exc.HTTPError,
                        status=418, status_int=418,
                        title='fake_title')

        self._on_error(
            response, exc, expected_status_code=exc.status,
            expected_body={'code': exc.status_int, 'title': exc.title}
        )

        self.CONF.set_override('app_dev_mode', True, 'api')
        self._on_error(
            response, exc, expected_status_code=exc.status,
            expected_body={'code': exc.status_int, 'title': exc.title,
                           'detail': str(exc)}
        )

    @mock.patch.object(webob, 'Response')
    def test_on_error_with_validation_error(self, response):
        self.CONF.set_override('app_dev_mode', False, 'api')
        exc = mock.Mock(spec=validators.ValidationError,
                        title='No No No!')

        self._on_error(
            response, exc, expected_status_code=400,
            expected_body={'code': 400, 'title': exc.title}
        )

        self.CONF.set_override('app_dev_mode', True, 'api')
        self._on_error(
            response, exc, expected_status_code=400,
            expected_body={'code': 400, 'title': exc.title,
                           'detail': str(exc)}
        )

    @mock.patch.object(webob, 'Response')
    def test_on_error_with_other_exceptions(self, response):
        self.CONF.set_override('app_dev_mode', False, 'api')
        exc = mock.Mock(status=500)

        self._on_error(
            response, exc, expected_status_code=500,
            expected_body={'code': 500, 'title': 'Internal Server Error'}
        )

        self.CONF.set_override('app_dev_mode', True, 'api')
        self._on_error(
            response, exc, expected_status_code=500,
            expected_body={'code': 500, 'title': 'Internal Server Error',
                           'detail': str(exc)}
        )


class SetupAppTestCase(base.BaseTestCase):

    def setUp(self):
        super(SetupAppTestCase, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

    @mock.patch('pecan.hooks')
    @mock.patch.object(app, 'JSONErrorHook')
    @mock.patch('os.path.join')
    @mock.patch('pecan.make_app')
    def test_setup_app(self, make_app, os_join,
                       json_error_hook, pecan_hooks):

        self.CONF.set_override('app_dev_mode',
                               True,
                               'api')
        self.CONF.set_override('template_path',
                               'fake_template_path',
                               'api')
        self.CONF.set_override('static_root',
                               'fake_static_root',
                               'api')

        os_join.return_value = 'fake_project_root'

        json_error_hook.return_value = 'json_error_hook'
        pecan_hooks.RequestViewerHook.return_value = 'request_viewer_hook'
        pecan_config = mock.Mock()
        pecan_config.app = {'root': 'fake_pecan_config'}
        make_app.return_value = 'fake_app'

        result = app.setup_app(pecan_config)

        self.assertEqual(result, 'fake_app')

        app_conf = dict(pecan_config.app)
        make_app.assert_called_once_with(
            app_conf.pop('root'),
            debug=True,
            static_root='fake_static_root',
            template_path='fake_template_path',
            hooks=['json_error_hook', 'request_viewer_hook']
        )
