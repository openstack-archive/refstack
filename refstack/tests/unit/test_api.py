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

import mock
from oslo_config import fixture as config_fixture
from six.moves.urllib import parse
import webob.exc

from refstack.api import constants as const
from refstack.api import exceptions as api_exc
from refstack.api.controllers import auth
from refstack.api.controllers import guidelines
from refstack.api.controllers import results
from refstack.api.controllers import user
from refstack.api.controllers import validation
from refstack.api.controllers import vendors
from refstack.tests import unit as base


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
                            return_value=True, spec=self.setUp)


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
        self.mock_get_user_role.return_value = const.ROLE_FOUNDATION
        test_info = {'created_at': 'bar',
                     'duration_seconds': 999,
                     'meta': {'shared': 'true', 'user': 'fake-user'}}
        mock_get_test.return_value = test_info

        mock_get_test_res.return_value = [{'name': 'test1'},
                                          {'name': 'test2'}]

        actual_result = self.controller.get_one('fake_arg')
        # All meta should be exposed when user is a Foundation admin.
        expected_result = {
            'created_at': 'bar',
            'duration_seconds': 999,
            'results': ['test1', 'test2'],
            'user_role': const.ROLE_FOUNDATION,
            'meta': {'shared': 'true', 'user': 'fake-user'}
        }

        self.assertEqual(expected_result, actual_result)
        mock_get_test_res.assert_called_once_with('fake_arg')

        # If not owner or Foundation admin, don't show all metadata.
        self.mock_get_user_role.return_value = const.ROLE_USER
        mock_get_test.return_value = test_info
        mock_get_test_res.return_value = [{'name': 'test1'},
                                          {'name': 'test2'}]
        actual_result = self.controller.get_one('fake_arg')
        expected_result['meta'] = {'shared': 'true'}
        expected_result['user_role'] = const.ROLE_USER
        self.assertEqual(expected_result, actual_result)

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
                                      'duration_seconds', 'meta',
                                      'product_version',
                                      'verification_status']
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

    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.api.utils.check_user_is_product_admin')
    @mock.patch('refstack.db.get_product_version_by_cpid')
    @mock.patch('refstack.db.store_results')
    @mock.patch('refstack.db.get_pubkey')
    def test_post_with_sign(self, mock_get_pubkey, mock_store_results,
                            mock_get_version, mock_check, mock_foundation):
        self.mock_request.body = '{"answer": 42, "cpid": "123"}'
        self.mock_request.headers = {
            'X-Signature': 'fake-sign',
            'X-Public-Key': 'ssh-rsa Zm9vIGJhcg=='
        }

        mock_get_pubkey.return_value.openid = 'fake_openid'
        mock_get_version.return_value = [{'id': 'ver1',
                                          'product_id': 'prod1'}]
        mock_check.return_value = True
        mock_foundation.return_value = False
        mock_store_results.return_value = 'fake_test_id'
        result = self.controller.post()
        self.assertEqual(result,
                         {'test_id': 'fake_test_id',
                          'url': self.test_results_url % 'fake_test_id'})
        self.assertEqual(self.mock_response.status, 201)
        mock_check.assert_called_once_with('prod1', 'fake_openid')
        mock_store_results.assert_called_once_with(
            {'answer': 42, 'cpid': '123', 'product_version_id': 'ver1',
             'meta': {const.USER: 'fake_openid'}}
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

    @mock.patch('refstack.api.utils.check_owner')
    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.db.get_test_records')
    @mock.patch('refstack.db.get_test_records_count')
    @mock.patch('refstack.api.utils.get_page_number')
    @mock.patch('refstack.api.utils.parse_input_params')
    def test_get_success(self,
                         parse_input,
                         get_page,
                         get_test_count,
                         db_get_test,
                         check_foundation,
                         check_owner):

        expected_input_params = [
            const.START_DATE,
            const.END_DATE,
            const.CPID,
            const.SIGNED,
            const.VERIFICATION_STATUS,
            const.PRODUCT_ID
        ]
        page_number = 1
        total_pages_number = 10
        per_page = 5
        records_count = 50
        get_test_count.return_value = records_count
        get_page.return_value = (page_number, total_pages_number)
        check_foundation.return_value = False
        check_owner.return_value = True
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
        self.assertEqual(expected_result, actual_result)

        parse_input.assert_called_once_with(expected_input_params)

        filters = parse_input.return_value
        get_test_count.assert_called_once_with(filters)
        get_page.assert_called_once_with(records_count)

        db_get_test.assert_called_once_with(page_number, per_page, filters)

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.delete_test')
    def test_delete(self, mock_db_delete, mock_get_test):
        self.mock_get_user_role.return_value = const.ROLE_OWNER

        self.controller.delete('test_id')
        self.assertEqual(204, self.mock_response.status)

        # Verified test deletion attempt should raise error.
        mock_get_test.return_value = {'verification_status':
                                      const.TEST_VERIFIED}
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'test_id')

        self.mock_get_user_role.return_value = const.ROLE_USER
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'test_id')


class GuidelinesControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(GuidelinesControllerTestCase, self).setUp()
        self.controller = guidelines.GuidelinesController()
        self.mock_abort.side_effect = None

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_list')
    def test_get_guidelines(self, mock_list):
        """Test when getting a list of all guideline files."""
        mock_list.return_value = ['2015.03.json']
        result = self.controller.get()
        self.assertEqual(['2015.03.json'], result)

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_list')
    def test_get_guidelines_error(self, mock_list):
        """Test when there is a problem getting the guideline list and
        nothing is returned."""
        mock_list.return_value = None
        self.controller.get()
        self.mock_abort.assert_called_with(500, mock.ANY)

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_contents')
    def test_get_guideline_file(self, mock_get_contents):
        """Test when getting a specific guideline file"""
        mock_get_contents.return_value = {'foo': 'bar'}
        result = self.controller.get_one('2015.03')
        self.assertEqual({'foo': 'bar'}, result)

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_contents')
    def test_get_guideline_file_error(self, mock_get_contents):
        """Test when there is a problem getting the guideline file contents."""
        mock_get_contents.return_value = None
        self.controller.get_one('2010.03')
        self.mock_abort.assert_called_with(500, mock.ANY)


class GuidelinesTestsControllerTestCase(BaseControllerTestCase):

    FAKE_GUIDELINES = {
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
                'advisory': [],
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

    def setUp(self):
        super(GuidelinesTestsControllerTestCase, self).setUp()
        self.controller = guidelines.TestsController()

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_contents')
    @mock.patch('pecan.request')
    def test_get_guideline_tests(self, mock_request, mock_get_contents):
        """Test getting the test list string of a guideline."""
        mock_get_contents.return_value = self.FAKE_GUIDELINES
        mock_request.GET = {}
        test_list_str = self.controller.get('2016,01')
        expected_list = ['test_1[id-1234]', 'test_2[id-5678]',
                         'test_2_1[id-5678]', 'test_3[id-1111]',
                         'test_4[id-1233]']
        expected_result = '\n'.join(expected_list)
        self.assertEqual(expected_result, test_list_str)

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_contents')
    def test_get_guideline_tests_fail(self, mock_get_contents):
        """Test when the JSON content of a guideline can't be retrieved."""
        mock_get_contents.return_value = None
        result_str = self.controller.get('2016.02')
        self.assertIn('Error getting JSON', result_str)

    @mock.patch('refstack.api.guidelines.Guidelines.get_guideline_contents')
    @mock.patch('pecan.request')
    def test_get_guideline_tests_invalid_target(self, mock_request,
                                                mock_get_contents):
        """Test when the target is invalid."""
        mock_get_contents.return_value = self.FAKE_GUIDELINES
        mock_request.GET = {'target': 'foo'}
        result_str = self.controller.get('2016.02')
        self.assertIn('Invalid target', result_str)


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

    @mock.patch('refstack.db.get_foundation_users',
                return_value=['foo@bar.org'])
    @mock.patch('refstack.db.user_get',
                return_value=mock.Mock(openid='foo@bar.org',
                                       email='foo@bar.org',
                                       fullname='Dobby'))
    @mock.patch('refstack.api.utils.get_user_session',
                return_value={const.USER_OPENID: 'foo@bar.org'})
    def test_get(self, mock_get_user_session, mock_user_get,
                 mock_get_foundation_users):
        actual_result = self.controller.get()
        self.assertEqual({'openid': 'foo@bar.org',
                          'email': 'foo@bar.org',
                          'fullname': 'Dobby',
                          'is_admin': True}, actual_result)


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
        mock_db_get_test.return_value = {'meta': {'shared': 'true',
                                                  'user': 'fake-user'}}
        # Only the key 'shared' should be allowed through.
        self.assertEqual({'shared': 'true'}, self.controller.get('test_id'))
        mock_db_get_test.assert_called_once_with('test_id')

        # Test that the result owner can see all metadata keys.
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        self.assertEqual({'shared': 'true', 'user': 'fake-user'},
                         self.controller.get('test_id'))

        # Test that a Foundation admin can see all metadata keys.
        self.mock_get_user_role.return_value = const.ROLE_FOUNDATION
        self.assertEqual({'shared': 'true', 'user': 'fake-user'},
                         self.controller.get('test_id'))

    @mock.patch('refstack.db.get_test_meta_key')
    def test_get_one(self, mock_db_get_test_meta_key):
        self.mock_get_user_role.return_value = const.ROLE_USER

        # Test when key is not an allowed key.
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.get_one, 'test_id', 'answer')

        # Test when key is an allowed key.
        mock_db_get_test_meta_key.return_value = 42
        self.assertEqual(42, self.controller.get_one('test_id', 'shared'))
        mock_db_get_test_meta_key.assert_called_once_with('test_id', 'shared')

        # Test when the user owns the test result.
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        self.assertEqual(42, self.controller.get_one('test_id', 'user'))

        # Test when the user is a Foundation admin.
        self.mock_get_user_role.return_value = const.ROLE_FOUNDATION
        self.assertEqual(42, self.controller.get_one('test_id', 'user'))

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.save_test_meta_item')
    def test_post(self, mock_save_test_meta_item, mock_get_test):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        mock_get_test.return_value = {
            'verification_status': const.TEST_NOT_VERIFIED
        }

        # Test trying to post a valid key.
        self.controller.post('test_id', 'shared')
        self.assertEqual(201, self.mock_response.status)
        mock_save_test_meta_item.assert_called_once_with(
            'test_id', 'shared', self.mock_request.body)

        # Test trying to post an invalid key.
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.post, 'test_id', 'user')

        # Test when not an owner of the result.
        self.mock_get_user_role.return_value = const.ROLE_USER
        self.mock_abort.side_effect = webob.exc.HTTPError()
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.post, 'test_id', 'shared')

    @mock.patch('refstack.db.get_test')
    @mock.patch('refstack.db.delete_test_meta_item')
    def test_delete(self, mock_delete_test_meta_item, mock_get_test):
        self.mock_get_user_role.return_value = const.ROLE_OWNER
        mock_get_test.return_value = {
            'verification_status': const.TEST_NOT_VERIFIED
        }
        self.controller.delete('test_id', 'shared')
        self.assertEqual(204, self.mock_response.status)
        mock_delete_test_meta_item.assert_called_once_with('test_id', 'shared')

        # The key 'user' is not a valid key that can be deleted.
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.delete, 'test_id', 'user')

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


class VendorUsersControllerTestCase(BaseControllerTestCase):

    def setUp(self):
        super(VendorUsersControllerTestCase, self).setUp()
        self.controller = vendors.UsersController()

    @mock.patch('refstack.db.get_organization_users')
    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.api.utils.check_user_is_vendor_admin')
    def test_get(self, mock_vendor, mock_foundation, mock_db_get_org_users):
        mock_vendor.return_value = True
        mock_foundation.return_value = False
        mock_db_get_org_users.return_value = {
            'foobar': {
                'openid': 'foobar',
                'fullname': 'Foo Bar',
                'email': 'foo@bar.com'
            }
        }
        expected = [{'openid': 'foobar',
                     'fullname': 'Foo Bar',
                     'email': 'foo@bar.com'}]
        self.assertEqual(expected, self.controller.get('some-org'))

        mock_vendor.return_value = False
        self.assertIsNone(self.controller.get('some-org'))

        mock_foundation.return_value = True
        self.assertEqual(expected, self.controller.get('some-org'))

    @mock.patch('refstack.db.add_user_to_group')
    @mock.patch('refstack.db.get_organization')
    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.api.utils.check_user_is_vendor_admin')
    @mock.patch('refstack.api.utils.get_user_id')
    def test_put(self, mock_get_user, mock_vendor, mock_foundation,
                 mock_db_org, mock_add):
        # This is 'foo' in Base64
        encoded_openid = 'Zm9v'
        mock_vendor.return_value = True
        mock_foundation.return_value = False
        mock_db_org.return_value = {'group_id': 'abc'}
        mock_get_user.return_value = 'fake-id'

        self.controller.put('fake-vendor', encoded_openid)
        mock_add.assert_called_once_with(b'foo', 'abc', 'fake-id')

        mock_vendor.return_value = False
        self.assertRaises(webob.exc.HTTPError,
                          self.controller.put, 'fake-vendor', encoded_openid)

    @mock.patch('refstack.db.remove_user_from_group')
    @mock.patch('refstack.db.get_organization')
    @mock.patch('refstack.api.utils.check_user_is_foundation_admin')
    @mock.patch('refstack.api.utils.check_user_is_vendor_admin')
    def test_delete(self, mock_vendor, mock_foundation, mock_db_org,
                    mock_remove):
        # This is 'foo' in Base64
        encoded_openid = 'Zm9v'
        mock_vendor.return_value = True
        mock_foundation.return_value = False
        mock_db_org.return_value = {'group_id': 'abc'}
        self.controller.delete('fake-vendor', encoded_openid)
        mock_remove.assert_called_with(b'foo', 'abc')

        mock_vendor.return_value = False
        self.assertRaises(webob.exc.HTTPError, self.controller.delete,
                          'fake-vendor', encoded_openid)
