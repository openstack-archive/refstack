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

"""Tests for API's controllers"""

import json
import sys

import httmock
import mock
from oslo_config import fixture as config_fixture
from oslotest import base
import requests
from six.moves.urllib import parse
import webob.exc

from refstack.api import constants as const
from refstack.api import utils as api_utils
from refstack.api.controllers import auth
from refstack.api.controllers import v1
from refstack.api.controllers import user


def safe_json_dump(content):
    if isinstance(content, (dict, list)):
        if sys.version_info[0] == 3:
            content = bytes(json.dumps(content), 'utf-8')
        else:
            content = json.dumps(content)
    return content


class RootControllerTestCase(base.BaseTestCase):

    @mock.patch('pecan.expose', return_value=lambda f: f)
    def test_index(self, expose_mock):
        config = config_fixture.Config()
        CONF = self.useFixture(config).conf
        CONF.set_override('app_dev_mode', True, 'api')
        from refstack.api.controllers import root
        controller = root.RootController()
        result = controller.index()
        self.assertEqual({}, result)
        expose_mock.assert_called_with(generic=True, template='index.html')


class ResultsControllerTestCase(base.BaseTestCase):

    def setUp(self):
        super(ResultsControllerTestCase, self).setUp()
        self.validator = mock.Mock()
        v1.ResultsController.__validator__ = \
            mock.Mock(exposed=False, return_value=self.validator)
        self.controller = v1.ResultsController()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf
        self.test_results_url = '/#/results/%s'
        self.ui_url = 'host.org'
        self.CONF.set_override('test_results_url',
                               self.test_results_url,
                               'api')
        self.CONF.set_override('ui_url', self.ui_url)

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.get_test_results')
    def test_get(self, mock_get_test_res, mock_get_test):
        self.validator.assert_id = mock.Mock(return_value=True)

        test_info = mock.Mock()
        test_info.cpid = 'foo'
        test_info.created_at = 'bar'
        test_info.duration_seconds = 999
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [('test1',), ('test2',), ('test3',)]

        actual_result = self.controller.get_one('fake_arg')
        expected_result = {
            'cpid': 'foo',
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2', 'test3']
        }

        self.assertEqual(actual_result, expected_result)
        mock_get_test_res.assert_called_once_with('fake_arg')
        mock_get_test.assert_called_once_with('fake_arg')
        self.validator.assert_id.assert_called_once_with('fake_arg')

    @mock.patch('refstack.db.store_results')
    @mock.patch('pecan.response')
    @mock.patch('pecan.request')
    def test_post(self, mock_request, mock_response, mock_store_results):
        mock_request.body = '{"answer": 42}'
        mock_request.headers = {}
        mock_store_results.return_value = 'fake_test_id'
        result = self.controller.post()
        self.assertEqual(
            result,
            {'test_id': 'fake_test_id',
             'url': parse.urljoin(self.ui_url,
                                  self.test_results_url) % 'fake_test_id'}
        )
        self.assertEqual(mock_response.status, 201)
        mock_store_results.assert_called_once_with({'answer': 42})

    @mock.patch('refstack.db.store_results')
    @mock.patch('pecan.response')
    @mock.patch('pecan.request')
    def test_post_with_sign(self, mock_request,
                            mock_response,
                            mock_store_results):
        mock_request.body = '{"answer": 42}'
        mock_request.headers = {
            'X-Signature': 'fake-sign',
            'X-Public-Key': 'fake-key'
        }
        mock_store_results.return_value = 'fake_test_id'
        result = self.controller.post()
        self.assertEqual(result,
                         {'test_id': 'fake_test_id',
                          'url': self.test_results_url % 'fake_test_id'})
        self.assertEqual(mock_response.status, 201)
        mock_store_results.assert_called_once_with(
            {'answer': 42, 'metadata': {'public_key': 'fake-key'}}
        )

    @mock.patch('pecan.abort')
    @mock.patch('refstack.db.get_test')
    def test_get_item_failed(self, mock_get_test, mock_abort):
        mock_get_test.return_value = None
        mock_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get_item,
                          'fake_id')

    @mock.patch('pecan.abort')
    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_failed_in_parse_input_params(self,
                                              parse_inputs,
                                              pecan_abort):

        parse_inputs.side_effect = api_utils.ParseInputsError()
        pecan_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('pecan.abort')
    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_failed_in_get_test_records_number(self,
                                                   parse_inputs,
                                                   pecan_abort,
                                                   db_get_count):
        db_get_count.side_effect = Exception()
        pecan_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.parse_input_params')
    @mock.patch('refstack.api.utils.get_page_number')
    @mock.patch('pecan.abort')
    def test_get_failed_in_get_page_number(self,
                                           pecan_abort,
                                           get_page,
                                           parse_input,
                                           db_get_count):

        get_page.side_effect = api_utils.ParseInputsError()
        pecan_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records')
    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.parse_input_params')
    @mock.patch('refstack.api.utils.get_page_number')
    @mock.patch('pecan.abort')
    def test_get_failed_in_get_test_records(self,
                                            pecan_abort,
                                            get_page,
                                            parce_input,
                                            db_get_count,
                                            db_get_test):

        get_page.return_value = (mock.Mock(), mock.Mock())
        db_get_test.side_effect = Exception()
        pecan_abort.side_effect = Exception()
        self.assertRaises(Exception,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records')
    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.get_page_number')
    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_success(self,
                         parse_input,
                         get_page,
                         get_test_count,
                         db_get_test):

        expected_input_params = [
            const.START_DATE,
            const.END_DATE,
            const.CPID,
        ]
        page_number = 1
        total_pages_number = 10
        per_page = 5
        records_count = 50
        get_test_count.return_value = records_count
        get_page.return_value = (page_number, total_pages_number)
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')

        record = mock.Mock()
        record.id = 111
        record.created_at = '12345'
        record.cpid = '54321'

        db_get_test.return_value = [record]
        expected_result = {
            'results': [{
                'test_id': record.id,
                'created_at': record.created_at,
                'cpid': record.cpid,
                'url': self.test_results_url % record.id
            }],
            'pagination': {
                'current_page': page_number,
                'total_pages': total_pages_number
            }
        }

        actual_result = self.controller.get()
        self.assertEqual(actual_result, expected_result)

        parse_input.assert_called_once_with(expected_input_params)

        filters = parse_input.return_value
        get_test_count.assert_called_once_with(filters)
        get_page.assert_called_once_with(records_count)

        db_get_test.assert_called_once_with(page_number, per_page, filters)


class CapabilitiesControllerTestCase(base.BaseTestCase):

    def setUp(self):
        super(CapabilitiesControllerTestCase, self).setUp()
        self.controller = v1.CapabilitiesController()

    def test_get_capabilities(self):
        """Test when getting a list of all capability files."""
        @httmock.all_requests
        def github_api_mock(url, request):
            headers = {'content-type': 'application/json'}
            content = [{'name': '2015.03.json', 'type': 'file'},
                       {'name': '2015.next.json', 'type': 'file'},
                       {'name': '2015.03', 'type': 'dir'}]
            content = safe_json_dump(content)
            return httmock.response(200, content, headers, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            result = self.controller.get()
        self.assertEqual(['2015.03.json'], result)

    @mock.patch('pecan.abort')
    def test_get_capabilities_error_code(self, mock_abort):
        """Test when the HTTP status code isn't a 200 OK. The status should
           be propogated."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            self.controller.get()
        mock_abort.assert_called_with(404)

    @mock.patch('requests.get')
    @mock.patch('pecan.abort')
    def test_get_capabilities_exception(self, mock_abort, mock_request):
        """Test when the GET request raises an exception."""
        mock_request.side_effect = requests.exceptions.RequestException()
        self.controller.get()
        mock_abort.assert_called_with(500)

    def test_get_capability_file(self):
        """Test when getting a specific capability file"""
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)

        with httmock.HTTMock(github_mock):
            result = self.controller.get_one('2015.03')
        self.assertEqual({'foo': 'bar'}, result)

    @mock.patch('pecan.abort')
    def test_get_capability_file_error_code(self, mock_abort):
        """Test when the HTTP status code isn't a 200 OK. The status should
           be propogated."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            self.controller.get_one('2010.03')
        mock_abort.assert_called_with(404)

    @mock.patch('requests.get')
    @mock.patch('pecan.abort')
    def test_get_capability_file_exception(self, mock_abort, mock_request):
        """Test when the GET request raises an exception."""
        mock_request.side_effect = requests.exceptions.RequestException()
        self.controller.get_one('2010.03')
        mock_abort.assert_called_with(500)


class BaseRestControllerWithValidationTestCase(base.BaseTestCase):

    def setUp(self):
        super(BaseRestControllerWithValidationTestCase, self).setUp()
        self.validator = mock.Mock()
        v1.BaseRestControllerWithValidation.__validator__ = \
            mock.Mock(exposed=False, return_value=self.validator)
        self.controller = v1.BaseRestControllerWithValidation()

    @mock.patch('pecan.response')
    @mock.patch('pecan.request')
    def test_post(self, mock_request, mock_response):
        mock_request.body = '[42]'
        self.controller.store_item = mock.Mock(return_value='fake_id')

        result = self.controller.post()

        self.assertEqual(result, 'fake_id')
        self.assertEqual(mock_response.status, 201)
        self.controller.store_item.assert_called_once_with([42])

    def test_get_one_return_item(self):
        self.validator.assert_id = mock.Mock(return_value=True)
        self.controller.get_item = mock.Mock(return_value='fake_item')

        result = self.controller.get_one('fake_arg')

        self.assertEqual(result, 'fake_item')
        self.validator.assert_id.assert_called_once_with('fake_arg')
        self.controller.get_item.assert_called_once_with(item_id='fake_arg')

    def test_get_one_return_schema(self):
        self.validator.assert_id = mock.Mock(return_value=False)
        self.validator.schema = 'fake_schema'
        result = self.controller.get_one('schema')
        self.assertEqual(result, 'fake_schema')

    @mock.patch('pecan.abort')
    def test_get_one_abort(self, mock_abort):
        self.validator.assert_id = mock.Mock(return_value=False)
        self.controller.get_one('fake_arg')
        mock_abort.assert_called_once_with(404)


class ProfileControllerTestCase(base.BaseTestCase):

    def setUp(self):
        super(ProfileControllerTestCase, self).setUp()
        self.controller = user.ProfileController()

    @mock.patch('refstack.db.user_get',
                return_value=mock.Mock(openid='foo@bar.org',
                                       email='foo@bar.org',
                                       fullname='Dobby'))
    @mock.patch('refstack.api.utils.get_user_session',
                return_value={const.USER_OPENID: 'foo@bar.org'})
    @mock.patch('refstack.api.utils.is_authenticated', return_value=True)
    def test_get(self, mock_is_authenticated, mock_get_user_session,
                 mock_user_get):
        actual_result = self.controller.get()
        self.assertEqual({'openid': 'foo@bar.org',
                          'email': 'foo@bar.org',
                          'fullname': 'Dobby'}, actual_result)


class AuthControllerTestCase(base.BaseTestCase):

    def setUp(self):
        super(AuthControllerTestCase, self).setUp()
        self.controller = auth.AuthController()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf
        self.CONF.set_override('app_dev_mode', True, 'api')
        self.CONF.set_override('ui_url', '127.0.0.1')

    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('refstack.api.utils.is_authenticated', return_value=True)
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signed_signin(self, mock_redirect, mock_is_authenticated,
                           mock_get_user_session):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org'})
        mock_get_user_session.return_value = mock_session
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signin)
        mock_redirect.assert_called_with('127.0.0.1')

    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('refstack.api.utils.is_authenticated', return_value=False)
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_unsigned_signin(self, mock_redirect, mock_is_authenticated,
                             mock_get_user_session):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org'})
        mock_get_user_session.return_value = mock_session
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signin)
        self.assertIn(self.CONF.osid.openstack_openid_endpoint,
                      mock_redirect.call_args[1]['location'])

    @mock.patch('socket.gethostbyname', return_value='1.1.1.1')
    @mock.patch('pecan.request')
    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.abort', side_effect=webob.exc.HTTPError)
    def test_signin_return_failed(self, mock_abort, mock_get_user_session,
                                  mock_request, mock_socket):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org',
                                         const.CSRF_TOKEN: '42'})
        mock_get_user_session.return_value = mock_session
        mock_request.remote_addr = '1.1.1.2'

        mock_request.GET = {
            const.OPENID_ERROR: 'foo is not bar!!!'
        }
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPError, self.controller.signin_return)
        mock_abort.assert_called_once_with(
            401, mock_request.GET[const.OPENID_ERROR])
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])

        mock_abort.reset_mock()
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        mock_request.GET = {
            const.OPENID_MODE: 'cancel'
        }
        self.assertRaises(webob.exc.HTTPError, self.controller.signin_return)
        mock_abort.assert_called_once_with(
            401, 'Authentication canceled.')
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])

        mock_abort.reset_mock()
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        mock_request.GET = {}
        self.assertRaises(webob.exc.HTTPError, self.controller.signin_return)
        mock_abort.assert_called_once_with(
            401, 'Authentication is failed. Try again.')
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])

        mock_abort.reset_mock()
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        mock_request.GET = {const.CSRF_TOKEN: '24'}
        mock_request.remote_addr = '1.1.1.1'
        self.assertRaises(webob.exc.HTTPError, self.controller.signin_return)
        mock_abort.assert_called_once_with(
            401, 'Authentication is failed. Try again.')
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])

    @mock.patch('refstack.api.utils.verify_openid_request', return_value=True)
    @mock.patch('refstack.db.user_update_or_create')
    @mock.patch('pecan.request')
    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signin_return_success(self, mock_redirect, mock_get_user_session,
                                   mock_request, mock_user, mock_verify):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org',
                                         const.CSRF_TOKEN: 42})
        mock_session.get = mock.Mock(return_value=42)
        mock_get_user_session.return_value = mock_session

        mock_request.GET = {
            const.OPENID_CLAIMED_ID: 'foo@bar.org',
            const.OPENID_NS_SREG_EMAIL: 'foo@bar.org',
            const.OPENID_NS_SREG_FULLNAME: 'foo',
            const.CSRF_TOKEN: 42
        }
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)

    @mock.patch('pecan.request')
    @mock.patch('refstack.api.utils.is_authenticated', return_value=True)
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signout(self, mock_redirect, mock_is_authenticated,
                     mock_request):
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signout)
        mock_redirect.assert_called_with('127.0.0.1')
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])
