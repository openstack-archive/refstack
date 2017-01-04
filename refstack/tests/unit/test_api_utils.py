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

"""Tests for API's utils"""
import time

import mock
from oslo_config import fixture as config_fixture
from oslo_utils import timeutils
from oslotest import base
from pecan import rest
import jwt
import six
from six.moves.urllib import parse
from webob import exc

from refstack.api import constants as const
from refstack.api import exceptions as api_exc
from refstack.api import utils as api_utils
from refstack import db

PRIV_KEY = '''-----BEGIN PRIVATE KEY-----
MIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEA2tgf+sqQ/aI7Cytr
cpQYzbpOk1xy9GQP+kFN8ewIJgSLKX9bJf+7YqRuK8vsdtmPWVaLZtKTpPnXL0lM
jMotYwIDAQABAkA1eKtPruEAZ/w/PWuygkcRNV1vmh4oYq6Yug4ed0qCZxPxkBNx
0nnK9LeiWDnSCQ/Fi46y7XS6BLsbZ2wqGarJAiEA+r6oaDqFoScgl7KyQfkIY7ph
bnlIxVm4HWCLwEH4020CIQDfbk76sO8NuUbSaU6tIAoF9jmtaSW7kMr8/7M+SISy
DwIhAKsUaLzsqP4iPyehoeRHcMTyhsWkdNVJ+Mf6dn+Pw6ElAiEAnHFgW6gHulRA
gpO5wv7sBcCiIgm9odeASiXAG5wrTYECIHKU0v03nQlGOL2HUognsEw/nihi/667
pcPXhEWd4qmC
-----END PRIVATE KEY-----'''

PUB_KEY = ('AAAAB3NzaC1yc2EAAAADAQABAAAAQQDa2B/6ypD9ojsLK2tylBjNuk6TXH'
           'L0ZA/6QU3x7AgmBIspf1sl/7tipG4ry+x22Y9ZVotm0pOk+dcvSUyMyi1j')


class APIUtilsTestCase(base.BaseTestCase):

    def setUp(self):
        super(APIUtilsTestCase, self).setUp()
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf

    @mock.patch('pecan.request')
    def test_get_input_params_from_request_all_results(self, mock_request):
        received_params = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:45',
            const.CPID: '12345',
        }

        expected_params = [
            const.START_DATE,
            const.END_DATE,
            const.CPID
        ]

        mock_request.GET = received_params

        result = api_utils._get_input_params_from_request(expected_params)

        self.assertEqual(result, received_params)

    @mock.patch('pecan.request')
    def test_get_input_params_from_request_partial_results(self,
                                                           mock_request):
        received_params = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:45',
            const.CPID: '12345',
        }

        expected_params = [
            const.START_DATE,
            const.END_DATE,
        ]

        expected_results = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:45',
        }

        mock_request.GET = received_params

        result = api_utils._get_input_params_from_request(expected_params)

        self.assertEqual(result, expected_results)

    @mock.patch('oslo_utils.timeutils.parse_strtime')
    @mock.patch.object(api_utils, '_get_input_params_from_request')
    def test_parse_input_params_failed_in_parse_time(self, mock_get_input,
                                                     mock_strtime):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.CONF.set_override('input_date_format',
                               fmt,
                               'api')
        raw_filters = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:45',
            const.CPID: '12345',
        }

        expected_params = mock.Mock()
        mock_get_input.return_value = raw_filters
        mock_strtime.side_effect = ValueError()
        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.parse_input_params,
                          expected_params)

    @mock.patch.object(api_utils, '_get_input_params_from_request')
    def test_parse_input_params_failed_in_compare_date(self, mock_get_input):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.CONF.set_override('input_date_format',
                               fmt,
                               'api')
        raw_filters = {
            const.START_DATE: '2015-03-26 15:04:50',
            const.END_DATE: '2015-03-26 15:04:40',
            const.CPID: '12345',
        }

        expected_params = mock.Mock()
        mock_get_input.return_value = raw_filters
        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.parse_input_params,
                          expected_params)

    @mock.patch.object(api_utils, '_get_input_params_from_request')
    @mock.patch.object(api_utils, 'is_authenticated', return_value=False)
    def test_parse_input_params_failed_in_auth(self, mock_is_authenticated,
                                               mock_get_input):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.CONF.set_override('input_date_format',
                               fmt,
                               'api')
        raw_filters = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:50',
            const.CPID: '12345',
            const.SIGNED: True
        }
        expected_params = mock.Mock()
        mock_get_input.return_value = raw_filters
        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.parse_input_params, expected_params)

    @mock.patch.object(api_utils, '_get_input_params_from_request')
    @mock.patch.object(api_utils, 'is_authenticated', return_value=True)
    @mock.patch.object(api_utils, 'get_user_id', return_value='fake_id')
    def test_parse_input_params_success(self,
                                        mock_get_user_id,
                                        mock_is_authenticated,
                                        mock_get_input):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.CONF.set_override('input_date_format',
                               fmt,
                               'api')
        raw_filters = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:50',
            const.CPID: '12345',
            const.SIGNED: True
        }

        expected_params = mock.Mock()
        mock_get_input.return_value = raw_filters

        parsed_start_date = timeutils.parse_strtime(
            raw_filters[const.START_DATE],
            fmt
        )

        parsed_end_date = timeutils.parse_strtime(
            raw_filters[const.END_DATE],
            fmt
        )

        expected_result = {
            const.START_DATE: parsed_start_date,
            const.END_DATE: parsed_end_date,
            const.CPID: '12345',
            const.SIGNED: True,
            const.OPENID: 'fake_id',
        }

        result = api_utils.parse_input_params(expected_params)
        self.assertEqual(expected_result, result)

        mock_get_input.assert_called_once_with(expected_params)

    def test_str_to_bool(self):
        self.assertTrue(api_utils.str_to_bool('True'))
        self.assertTrue(api_utils.str_to_bool('1'))
        self.assertTrue(api_utils.str_to_bool('YES'))
        self.assertFalse(api_utils.str_to_bool('False'))
        self.assertFalse(api_utils.str_to_bool('no'))

    def test_calculate_pages_number_full_pages(self):
        # expected pages number: 20/10 = 2
        page_number = api_utils._calculate_pages_number(10, 20)
        self.assertEqual(page_number, 2)

    def test_calculate_pages_number_half_page(self):
        # expected pages number: 25/10
        # => quotient == 2 and remainder == 5
        # => total number of pages == 3
        page_number = api_utils._calculate_pages_number(10, 25)
        self.assertEqual(page_number, 3)

    @mock.patch('pecan.request')
    def test_get_page_number_page_number_is_none(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: None
        }

        page_number, total_pages = api_utils.get_page_number(total_records)

        self.assertEqual(page_number, 1)
        self.assertEqual(total_pages, total_records / per_page)

    @mock.patch('pecan.request')
    def test_get_page_number_page_number_not_int(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: 'abc'
        }

        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.get_page_number,
                          total_records)

    @mock.patch('pecan.request')
    def test_get_page_number_page_number_is_one(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: '1'
        }

        page_number, total_pages = api_utils.get_page_number(total_records)

        self.assertEqual(page_number, 1)
        self.assertEqual(total_pages, total_records / per_page)

    @mock.patch('pecan.request')
    def test_get_page_number_page_number_less_zero(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: '-1'
        }

        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.get_page_number,
                          total_records)

    @mock.patch('pecan.request')
    def test_get_page_number_page_number_more_than_total(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: '100'
        }

        self.assertRaises(api_exc.ParseInputsError,
                          api_utils.get_page_number,
                          total_records)

    @mock.patch('pecan.request')
    def test_get_page_number_success(self, mock_request):
        per_page = 20
        total_records = 100
        self.CONF.set_override('results_per_page',
                               per_page,
                               'api')
        mock_request.GET = {
            const.PAGE: '2'
        }

        page_number, total_pages = api_utils.get_page_number(total_records)

        self.assertEqual(page_number, 2)
        self.assertEqual(total_pages, total_records / per_page)

    def test_set_query_params(self):
        url = 'http://e.io/path#fragment'
        new_url = api_utils.set_query_params(url, {'foo': 'bar', '?': 42})
        self.assertEqual(parse.parse_qs(parse.urlparse(new_url)[4]),
                         {'foo': ['bar'], '?': ['42']})

    def test_get_token(self):
        token = api_utils.get_token(42)
        self.assertRegexpMatches(token, "[a-z]{42}")

    @mock.patch.object(api_utils, 'get_user_session')
    def test_delete_params_from_user_session(self, mock_get_user_session):
        mock_session = mock.MagicMock(**{'foo': 'bar', 'answer': 42})
        mock_get_user_session.return_value = mock_session
        api_utils.delete_params_from_user_session(('foo', 'answer'))
        self.assertNotIn('foo', mock_session.__dir__)
        self.assertNotIn('answer', mock_session.__dir__)
        mock_session.save.called_once_with()

    @mock.patch('pecan.request')
    def test_get_user_session(self, mock_request):
        mock_request.environ = {'beaker.session': 42}
        session = api_utils.get_user_session()
        self.assertEqual(42, session)

    @mock.patch.object(api_utils, 'get_user_session')
    @mock.patch.object(api_utils, 'db')
    @mock.patch('pecan.request')
    def test_is_authenticated(self, mock_request,
                              mock_db, mock_get_user_session):
        mock_request.headers = {}
        mock_session = {const.USER_OPENID: 'foo@bar.com'}
        mock_get_user_session.return_value = mock_session
        mock_get_user = mock_db.user_get
        mock_get_user.return_value = 'FAKE_USER'
        self.assertTrue(api_utils.is_authenticated())
        mock_db.user_get.assert_called_once_with('foo@bar.com')

        mock_request.environ = {
            const.JWT_TOKEN_ENV: {const.USER_OPENID: 'foo@bar.com'}}
        mock_get_user_session.return_value = {}
        mock_get_user.reset_mock()
        mock_get_user.return_value = 'FAKE_USER'
        self.assertTrue(api_utils.is_authenticated())
        mock_get_user.assert_called_once_with('foo@bar.com')

        mock_db.NotFound = db.NotFound
        mock_get_user.side_effect = mock_db.NotFound('User')
        self.assertFalse(api_utils.is_authenticated())

    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('pecan.abort', side_effect=exc.HTTPError)
    @mock.patch('refstack.db.get_test_meta_key')
    @mock.patch('refstack.db.get_test')
    @mock.patch.object(api_utils, 'is_authenticated')
    @mock.patch.object(api_utils, 'get_user_id')
    def test_check_get_user_role(self, mock_get_user_id,
                                 mock_is_authenticated,
                                 mock_get_test,
                                 mock_get_test_meta_key,
                                 mock_pecan_abort,
                                 mock_check_foundation):
        # Check user level
        mock_check_foundation.return_value = False
        mock_get_test_meta_key.return_value = None
        mock_get_test.return_value = {}
        self.assertEqual(const.ROLE_USER, api_utils.get_user_role('fake_test'))
        api_utils.enforce_permissions('fake_test', const.ROLE_USER)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_OWNER)

        mock_get_test_meta_key.side_effect = {
            ('fake_test', const.USER): 'fake_openid',
            ('fake_test', const.SHARED_TEST_RUN): 'true',
        }.get
        self.assertEqual(const.ROLE_USER, api_utils.get_user_role('fake_test'))
        api_utils.enforce_permissions('fake_test', const.ROLE_USER)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_OWNER)

        mock_is_authenticated.return_value = True
        mock_get_user_id.return_value = 'fake_openid'
        mock_get_test_meta_key.side_effect = {
            ('fake_test', const.USER): 'fake_openid',
            ('fake_test', const.SHARED_TEST_RUN): 'true',
        }.get
        self.assertEqual(const.ROLE_USER, api_utils.get_user_role('fake_test'))
        api_utils.enforce_permissions('fake_test', const.ROLE_USER)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_OWNER)

        # Check owner level
        mock_is_authenticated.return_value = True
        mock_get_user_id.return_value = 'fake_openid'
        mock_get_test_meta_key.side_effect = lambda *args: {
            ('fake_test', const.USER): 'fake_openid',
            ('fake_test', const.SHARED_TEST_RUN): None,
        }.get(args)
        self.assertEqual(const.ROLE_OWNER,
                         api_utils.get_user_role('fake_test'))
        api_utils.enforce_permissions('fake_test', const.ROLE_USER)
        api_utils.enforce_permissions('fake_test', const.ROLE_OWNER)

        # Check negative cases
        mock_is_authenticated.return_value = False
        mock_get_test_meta_key.side_effect = lambda *args: {
            ('fake_test', const.USER): 'fake_openid',
            ('fake_test', const.SHARED_TEST_RUN): None,
        }.get(args)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_USER)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_OWNER)

        mock_is_authenticated.return_value = True
        mock_get_user_id.return_value = 'fake_openid'
        mock_get_test_meta_key.side_effect = lambda *args: {
            ('fake_test', const.USER): 'some_other_user',
            ('fake_test', const.SHARED_TEST_RUN): None,
        }.get(args)
        self.assertIsNone(api_utils.get_user_role('fake_test'))
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_USER)
        self.assertRaises(exc.HTTPError, api_utils.enforce_permissions,
                          'fake_test', const.ROLE_OWNER)

    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('pecan.abort', side_effect=exc.HTTPError)
    @mock.patch('refstack.db.get_test_meta_key')
    @mock.patch('refstack.db.get_test')
    @mock.patch.object(api_utils, 'is_authenticated')
    @mock.patch.object(api_utils, 'get_user_id')
    def test_check_permissions(self, mock_get_user_id,
                               mock_is_authenticated,
                               mock_get_test,
                               mock_get_test_meta_key,
                               mock_pecan_abort,
                               mock_foundation_check):

        @api_utils.check_permissions(level=const.ROLE_USER)
        class ControllerWithPermissions(rest.RestController):

            def get(self, test_id):
                return test_id

            @api_utils.check_permissions(level=const.ROLE_OWNER)
            def delete(self, test_id):
                return test_id

            @api_utils.check_permissions(level='fake_role')
            def post(self, test_id):
                return test_id

        fake_controller = ControllerWithPermissions()

        public_test = 'fake_public_test'
        private_test = 'fake_test'

        mock_get_user_id.return_value = 'fake_openid'
        mock_get_test.return_value = {}
        mock_get_test_meta_key.side_effect = lambda *args: {
            (public_test, const.USER): None,
            (private_test, const.USER): 'fake_openid',
            (private_test, const.SHARED_TEST_RUN): None,
        }.get(args)

        mock_is_authenticated.return_value = True
        mock_foundation_check.return_value = False
        self.assertEqual(public_test, fake_controller.get(public_test))
        self.assertRaises(exc.HTTPError, fake_controller.delete, public_test)
        self.assertEqual(private_test, fake_controller.get(private_test))
        self.assertEqual(private_test, fake_controller.delete(private_test))

        mock_is_authenticated.return_value = False
        self.assertEqual(public_test, fake_controller.get(public_test))
        self.assertRaises(exc.HTTPError, fake_controller.delete, public_test)
        self.assertRaises(exc.HTTPError, fake_controller.get, private_test)
        self.assertRaises(exc.HTTPError, fake_controller.delete, private_test)

        self.assertRaises(ValueError, fake_controller.post, public_test)

    @mock.patch('requests.post')
    @mock.patch('pecan.abort')
    def test_verify_openid_request(self, mock_abort, mock_post):
        mock_response = mock.Mock()
        mock_response.content = ('is_valid:true\n'
                                 'ns:http://specs.openid.net/auth/2.0\n')
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        mock_request = mock.Mock()
        mock_request.params = {
            const.OPENID_NS_SREG_EMAIL: 'foo@bar.org',
            const.OPENID_NS_SREG_FULLNAME: 'foo'
        }
        self.assertTrue(api_utils.verify_openid_request(mock_request))

        mock_response.content = ('is_valid:false\n'
                                 'ns:http://specs.openid.net/auth/2.0\n')
        api_utils.verify_openid_request(mock_request)
        mock_abort.assert_called_once_with(
            401, 'Authentication is failed. Try again.'
        )

        mock_abort.reset_mock()
        mock_response.content = ('is_valid:true\n'
                                 'ns:http://specs.openid.net/auth/2.0\n')
        mock_request.params = {
            const.OPENID_NS_SREG_EMAIL: 'foo@bar.org',
        }
        api_utils.verify_openid_request(mock_request)
        mock_abort.assert_called_once_with(
            401, 'Authentication is failed. '
                 'Please permit access to your name.'
        )

    @mock.patch('refstack.db.get_organization_users')
    @mock.patch.object(api_utils, 'get_user_id', return_value='fake_id')
    def test_check_user_is_vendor_admin(self, mock_user, mock_db):
        mock_user.return_value = 'some-user'
        mock_db.return_value = ['some-user', 'another-user']
        result = api_utils.check_user_is_vendor_admin('some-vendor')
        self.assertTrue(result)

        mock_db.return_value = ['another-user']
        result = api_utils.check_user_is_vendor_admin('some-vendor')
        self.assertFalse(result)

    @mock.patch('refstack.db.get_user_pubkeys')
    def test_encode_token(self, mock_pubkey):
        mock_request = mock.MagicMock()
        mock_request.headers = {}
        self.assertIsNone(api_utils.decode_token(mock_request))

        fake_token = jwt.encode({'foo': 'bar'}, key=PRIV_KEY,
                                algorithm='RS256')
        auth_str = 'Bearer %s' % six.text_type(fake_token, 'utf-8')
        mock_request.headers = {const.JWT_TOKEN_HEADER: auth_str}
        self.assertRaises(api_exc.ValidationError, api_utils.decode_token,
                          mock_request)

        fake_token = jwt.encode({const.USER_OPENID: 'oid'}, key=PRIV_KEY,
                                algorithm='RS256')
        auth_str = 'Bearer %s' % six.text_type(fake_token, 'utf-8')
        mock_request.headers = {const.JWT_TOKEN_HEADER: auth_str}
        mock_pubkey.return_value = [{'format': 'ssh-rsa',
                                     'pubkey': 'fakepubkey'}]
        self.assertRaises(api_exc.ValidationError, api_utils.decode_token,
                          mock_request)

        mock_pubkey.return_value = [{'format': 'ssh-rsa',
                                     'pubkey': PUB_KEY}]
        self.assertRaises(api_exc.ValidationError, api_utils.decode_token,
                          mock_request)

        fake_token = jwt.encode({const.USER_OPENID: 'oid',
                                 'exp': int(time.time()) + 3600},
                                key=PRIV_KEY,
                                algorithm='RS256')
        auth_str = 'Bearer %s' % six.text_type(fake_token, 'utf-8')
        mock_request.headers = {const.JWT_TOKEN_HEADER: auth_str}
        mock_pubkey.return_value = [{'format': 'ssh-rsa',
                                     'pubkey': PUB_KEY}]
        self.assertEqual('oid',
                         api_utils.decode_token(
                             mock_request)[const.USER_OPENID])
