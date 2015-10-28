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
import requests
from six.moves.urllib import parse
import webob.exc

from refstack.api import constants as const
from refstack.api import exceptions as api_exc
from refstack.api.controllers import auth
from refstack.api.controllers import capabilities
from refstack.api.controllers import results
from refstack.api.controllers import validation
from refstack.api.controllers import user
from refstack.tests import unit as base


def safe_json_dump(content):
    if isinstance(content, (dict, list)):
        if sys.version_info[0] == 3:
            content = bytes(json.dumps(content), 'utf-8')
        else:
            content = json.dumps(content)
    return content


class BaseControllerTestCase(base.RefstackBaseTestCase):

    def setUp(self):
        super(BaseControllerTestCase, self).setUp()
        self.mock_request = self.setup_mock('pecan.request')
        self.mock_response = self.setup_mock('pecan.response')
        self.mock_abort = \
            self.setup_mock('pecan.abort',
                            side_effect=webob.exc.HTTPError)
        self.mock_get_user_role = \
            self.setup_mock('refstack.api.utils.get_user_role')
        self.mock_is_authenticated = \
            self.setup_mock('refstack.api.utils.is_authenticated',
                            return_value=True)


class RootControllerTestCase(BaseControllerTestCase):

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


class ResultsControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(ResultsControllerTestCase, self).setUp()
        self.validator = mock.Mock()
        results.ResultsController.__validator__ = \
            mock.Mock(exposed=False, return_value=self.validator)
        self.controller = results.ResultsController()
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
        self.mock_get_user_role.return_value = const.ROLE_USER
        test_info = {'created_at': 'bar',
                     'duration_seconds': 999}
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [{'name': 'test1'},
                                          {'name': 'test2'}]

        actual_result = self.controller.get_one('fake_arg')
        expected_result = {
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2'],
            'user_role': const.ROLE_USER
        }

        self.assertEqual(actual_result, expected_result)
        mock_get_test_res.assert_called_once_with('fake_arg')
        mock_get_test.assert_called_once_with('fake_arg')

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.get_test_results')
    def test_get_for_owner(self, mock_get_test_res, mock_get_test):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        test_info = {'cpid': 'foo',
                     'created_at': 'bar',
                     'duration_seconds': 999}
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [{'name': 'test1'},
                                          {'name': 'test2'}]

        actual_result = self.controller.get_one('fake_arg')
        expected_result = {
            'cpid': 'foo',
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2'],
            'user_role': const.ROLE_OWNER
        }

        self.assertEqual(actual_result, expected_result)
        mock_get_test_res.assert_called_once_with('fake_arg')
        mock_get_test.assert_called_once_with(
            'fake_arg', allowed_keys=['id', 'cpid', 'created_at',
                                      'duration_seconds', 'meta']
        )

    @mock.patch('refstack.db.store_results')
    def test_post(self, mock_store_results):
        self.mock_request.body = '{"answer": 42}'
        self.mock_request.headers = {}
        mock_store_results.return_value = 'fake_test_id'
        result = self.controller.post()
        self.assertEqual(
            result,
            {'test_id': 'fake_test_id',
             'url': parse.urljoin(self.ui_url,
                                  self.test_results_url) % 'fake_test_id'}
        )
        self.assertEqual(self.mock_response.status, 201)
        mock_store_results.assert_called_once_with({'answer': 42})

    @mock.patch('refstack.db.store_results')
    def test_post_with_sign(self, mock_store_results):
        self.mock_request.body = '{"answer": 42}'
        self.mock_request.headers = {
            'X-Signature': 'fake-sign',
            'X-Public-Key': 'fake-key'
        }
        mock_store_results.return_value = 'fake_test_id'
        result = self.controller.post()
        self.assertEqual(result,
                         {'test_id': 'fake_test_id',
                          'url': self.test_results_url % 'fake_test_id'})
        self.assertEqual(self.mock_response.status, 201)
        mock_store_results.assert_called_once_with(
            {'answer': 42, 'meta': {const.PUBLIC_KEY: 'fake-key'}}
        )

    @mock.patch('refstack.db.get_test')
    def test_get_item_failed(self, mock_get_test):
        mock_get_test.return_value = None
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.get_one,
                          'fake_id')

    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_failed_in_parse_input_params(self, parse_inputs):

        parse_inputs.side_effect = api_exc.ParseInputsError()
        self.assertRaises(api_exc.ParseInputsError,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_failed_in_get_test_records_number(self,
                                                   parse_inputs,
                                                   db_get_count):
        db_get_count.side_effect = api_exc.ParseInputsError()
        self.assertRaises(api_exc.ParseInputsError,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.parse_input_params')
    @mock.patch('refstack.api.utils.get_page_number')
    def test_get_failed_in_get_page_number(self,
                                           get_page,
                                           parse_input,
                                           db_get_count):

        get_page.side_effect = api_exc.ParseInputsError()
        self.assertRaises(api_exc.ParseInputsError,
                          self.controller.get)

    @mock.patch('refstack.db.get_test_records')
    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.parse_input_params')
    @mock.patch('refstack.api.utils.get_page_number')
    def test_get_failed_in_get_test_records(self,
                                            get_page,
                                            parce_input,
                                            db_get_count,
                                            db_get_test):

        get_page.return_value = (mock.Mock(), mock.Mock())
        db_get_test.side_effect = Exception()
        self.assertRaises(webob.exc.HTTPError,
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
            const.SIGNED
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

        record = {'id': 111, 'created_at': '12345', 'cpid': '54321'}
        expected_record = record.copy()
        expected_record['url'] = self.test_results_url % record['id']

        db_get_test.return_value = [record]
        expected_result = {
            'results': [expected_record],
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

    @mock.patch('refstack.db.delete_test')
    def test_delete(self, mock_db_delete):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        self.controller.delete('test_id')
        self.assertEqual(204, self.mock_response.status)
        self.mock_get_user_role.return_value = const.ROLE_USER
        self.mock_abort.side_effect = webob.exc.HTTPError()
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'test_id')


class CapabilitiesControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(CapabilitiesControllerTestCase, self).setUp()
        self.controller = capabilities.CapabilitiesController()
        self.mock_abort.side_effect = None

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

    def test_get_capabilities_error_code(self):
        """Test when the HTTP status code isn't a 200 OK. The status should
           be propogated."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            self.controller.get()
        self.mock_abort.assert_called_with(404)

    @mock.patch('requests.get')
    def test_get_capabilities_exception(self, mock_requests_get):
        """Test when the GET request raises an exception."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.controller.get()
        self.mock_abort.assert_called_with(500)

    def test_get_capability_file(self):
        """Test when getting a specific capability file"""
        @httmock.all_requests
        def github_mock(url, request):
            content = {'foo': 'bar'}
            return httmock.response(200, content, None, None, 5, request)

        with httmock.HTTMock(github_mock):
            result = self.controller.get_one('2015.03')
        self.assertEqual({'foo': 'bar'}, result)

    def test_get_capability_file_error_code(self):
        """Test when the HTTP status code isn't a 200 OK. The status should
           be propogated."""
        @httmock.all_requests
        def github_api_mock(url, request):
            content = {'title': 'Not Found'}
            return httmock.response(404, content, None, None, 5, request)

        with httmock.HTTMock(github_api_mock):
            self.controller.get_one('2010.03')
        self.mock_abort.assert_called_with(404)

    @mock.patch('requests.get')
    def test_get_capability_file_exception(self, mock_requests_get):
        """Test when the GET request raises an exception."""
        mock_requests_get.side_effect = requests.exceptions.RequestException()
        self.controller.get_one('2010.03')
        self.mock_abort.assert_called_with(500)


class BaseRestControllerWithValidationTestCase(BaseControllerTestCase):

    def setUp(self):
        super(BaseRestControllerWithValidationTestCase, self).setUp()
        self.validator = mock.Mock()
        validation.BaseRestControllerWithValidation.__validator__ = \
            mock.Mock(exposed=False, return_value=self.validator)
        self.controller = validation.BaseRestControllerWithValidation()

    @mock.patch('pecan.response')
    @mock.patch('pecan.request')
    def test_post(self, mock_request, mock_response):
        mock_request.body = '[42]'
        self.controller.store_item = mock.Mock(return_value='fake_id')

        result = self.controller.post()

        self.assertEqual(result, 'fake_id')
        self.assertEqual(mock_response.status, 201)
        self.controller.store_item.assert_called_once_with([42])

    def test_get_one_return_schema(self):
        self.validator.assert_id = mock.Mock(return_value=False)
        self.validator.schema = 'fake_schema'
        result = self.controller.schema()
        self.assertEqual(result, 'fake_schema')


class ProfileControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(ProfileControllerTestCase, self).setUp()
        self.controller = user.ProfileController()

    @mock.patch('refstack.db.user_get',
                return_value=mock.Mock(openid='foo@bar.org',
                                       email='foo@bar.org',
                                       fullname='Dobby'))
    @mock.patch('refstack.api.utils.get_user_session',
                return_value={const.USER_OPENID: 'foo@bar.org'})
    def test_get(self, mock_get_user_session, mock_user_get):
        actual_result = self.controller.get()
        self.assertEqual({'openid': 'foo@bar.org',
                          'email': 'foo@bar.org',
                          'fullname': 'Dobby'}, actual_result)


class AuthControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(AuthControllerTestCase, self).setUp()
        self.controller = auth.AuthController()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf
        self.CONF.set_override('app_dev_mode', True, 'api')
        self.CONF.set_override('ui_url', 'http://127.0.0.1')
        self.CONF.set_override('openid_logout_endpoint', 'http://some-url',
                               'osid')

    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signed_signin(self, mock_redirect, mock_get_user_session):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org'})
        mock_get_user_session.return_value = mock_session
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signin)
        mock_redirect.assert_called_with('http://127.0.0.1')

    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_unsigned_signin(self, mock_redirect, mock_get_user_session):
        self.mock_is_authenticated.return_value = False
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org'})
        mock_get_user_session.return_value = mock_session
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signin)
        self.assertIn(self.CONF.osid.openstack_openid_endpoint,
                      mock_redirect.call_args[1]['location'])

    @mock.patch('socket.gethostbyname', return_value='1.1.1.1')
    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signin_return_failed(self, mock_redirect,
                                  mock_get_user_session,
                                  mock_socket):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org',
                                         const.CSRF_TOKEN: '42'})
        mock_get_user_session.return_value = mock_session
        self.mock_request.remote_addr = '1.1.1.2'

        self.mock_request.GET = {
            const.OPENID_ERROR: 'foo is not bar!!!'
        }
        self.mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)
        mock_redirect.assert_called_once_with(
            'http://127.0.0.1/#/auth_failure?message=foo+is+not+bar%21%21%21')
        self.assertNotIn(const.CSRF_TOKEN,
                         self.mock_request.environ['beaker.session'])

        mock_redirect.reset_mock()
        self.mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.mock_request.GET = {
            const.OPENID_MODE: 'cancel'
        }
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)
        mock_redirect.assert_called_once_with(
            'http://127.0.0.1/#/auth_failure?message=Authentication+canceled.')
        self.assertNotIn(const.CSRF_TOKEN,
                         self.mock_request.environ['beaker.session'])

        mock_redirect.reset_mock()
        self.mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.mock_request.GET = {}
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)
        mock_redirect.assert_called_once_with(
            'http://127.0.0.1/#/auth_failure'
            '?message=Authentication+failed.+Please+try+again.')
        self.assertNotIn(const.CSRF_TOKEN,
                         self.mock_request.environ['beaker.session'])

        mock_redirect.reset_mock()
        self.mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.mock_request.GET = {const.CSRF_TOKEN: '24'}
        self.mock_request.remote_addr = '1.1.1.1'
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)
        mock_redirect.assert_called_once_with(
            'http://127.0.0.1/#/auth_failure'
            '?message=Authentication+failed.+Please+try+again.')
        self.assertNotIn(const.CSRF_TOKEN,
                         self.mock_request.environ['beaker.session'])

    @mock.patch('refstack.api.utils.verify_openid_request', return_value=True)
    @mock.patch('refstack.db.user_save')
    @mock.patch('refstack.api.utils.get_user_session')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signin_return_success(self, mock_redirect, mock_get_user_session,
                                   mock_user, mock_verify):
        mock_session = mock.MagicMock(**{const.USER_OPENID: 'foo@bar.org',
                                         const.CSRF_TOKEN: 42})
        mock_session.get = mock.Mock(return_value=42)
        mock_get_user_session.return_value = mock_session

        self.mock_request.GET = {
            const.OPENID_CLAIMED_ID: 'foo@bar.org',
            const.OPENID_NS_SREG_EMAIL: 'foo@bar.org',
            const.OPENID_NS_SREG_FULLNAME: 'foo',
            const.CSRF_TOKEN: 42
        }
        self.mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPRedirection,
                          self.controller.signin_return)

    @mock.patch('pecan.request')
    @mock.patch('pecan.redirect', side_effect=webob.exc.HTTPRedirection)
    def test_signout(self, mock_redirect, mock_request):
        mock_request.environ['beaker.session'] = {
            const.CSRF_TOKEN: 42
        }
        self.assertRaises(webob.exc.HTTPRedirection, self.controller.signout)
        mock_redirect.assert_called_with('http://127.0.0.1/#/logout?'
                                         'openid_logout=http%3A%2F%2Fsome-url')
        self.assertNotIn(const.CSRF_TOKEN,
                         mock_request.environ['beaker.session'])


class MetadataControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(MetadataControllerTestCase, self).setUp()
        self.controller = results.MetadataController()

    @mock.patch('refstack.db.get_test')
    def test_get(self, mock_db_get_test):
        self.mock_get_user_role.return_value = const.ROLE_USER
        mock_db_get_test.return_value = {'meta': 'fake_meta'}
        self.assertEqual('fake_meta', self.controller.get('test_id'))
        mock_db_get_test.assert_called_once_with('test_id')

    @mock.patch('refstack.db.get_test_meta_key')
    def test_get_one(self, mock_db_get_test_meta_key):
        self.mock_get_user_role.return_value = const.ROLE_USER
        mock_db_get_test_meta_key.return_value = 42
        self.assertEqual(42, self.controller.get_one('test_id', 'answer'))
        mock_db_get_test_meta_key.assert_called_once_with('test_id', 'answer')

    @mock.patch('refstack.db.save_test_meta_item')
    def test_post(self, mock_save_test_meta_item):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        self.controller.post('test_id', 'answer')
        self.assertEqual(201, self.mock_response.status)
        mock_save_test_meta_item.assert_called_once_with(
            'test_id', 'answer', self.mock_request.body)

        self.mock_get_user_role.return_value = const.ROLE_USER
        self.mock_abort.side_effect = webob.exc.HTTPError()
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.post, 'test_id', 'answer')

    @mock.patch('refstack.db.delete_test_meta_item')
    def test_delete(self, mock_delete_test_meta_item):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        self.controller.delete('test_id', 'answer')
        self.assertEqual(204, self.mock_response.status)
        mock_delete_test_meta_item.assert_called_once_with('test_id', 'answer')

        self.mock_get_user_role.return_value = const.ROLE_USER
        self.mock_abort.side_effect = webob.exc.HTTPError()
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'test_id', 'answer')


class PublicKeysControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(PublicKeysControllerTestCase, self).setUp()
        self.controller = user.PublicKeysController()

    @mock.patch('refstack.api.utils.get_user_public_keys')
    def test_get(self, mock_get_user_public_keys):
        mock_get_user_public_keys.return_value = 42
        self.assertEqual(42, self.controller.get())
        mock_get_user_public_keys.assert_called_once_with()

    @mock.patch('refstack.api.utils.get_user_id')
    @mock.patch('refstack.db.store_pubkey')
    def test_post(self, mock_store_pubkey, mock_get_user_id):
        self.controller.validator.validate = mock.Mock()
        mock_get_user_id.return_value = 'fake_id'
        mock_store_pubkey.return_value = 42
        raw_key = 'fake key Don\'t_Panic.'
        fake_pubkey = {
            'format': 'fake',
            'pubkey': 'key',
            'comment': 'Don\'t_Panic.',
            'openid': 'fake_id'
        }
        self.mock_request.body = json.dumps({'raw_key': raw_key})
        self.controller.post()
        self.assertEqual(201, self.mock_response.status)
        mock_store_pubkey.assert_called_once_with(fake_pubkey)
        mock_store_pubkey.reset_mock()

        raw_key = 'fake key'
        fake_pubkey = {
            'format': 'fake',
            'pubkey': 'key',
            'comment': '',
            'openid': 'fake_id'
        }
        self.mock_request.body = json.dumps({'raw_key': raw_key})
        self.controller.post()
        mock_store_pubkey.assert_called_once_with(fake_pubkey)

    @mock.patch('refstack.db.delete_pubkey')
    @mock.patch('refstack.api.utils.get_user_public_keys')
    def test_delete(self, mock_get_user_public_keys, mock_delete_pubkey):
        mock_get_user_public_keys.return_value = ({'id': 'key_id'},)
        self.controller.delete('key_id')
        self.assertEqual(204, self.mock_response.status)
        mock_delete_pubkey.assert_called_once_with('key_id')

        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'other_key_id')
