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

"""Refstack API's utils."""
import binascii
import copy
import functools
import random
import requests
import string
import types

from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization
from oslo_config import cfg
from oslo_log import log
from oslo_utils import timeutils
import pecan
import pecan.rest
import jwt
import six
from six.moves.urllib import parse

from refstack import db
from refstack.api import constants as const
from refstack.api import exceptions as api_exc

LOG = log.getLogger(__name__)
CONF = cfg.CONF


def _get_input_params_from_request(expected_params):
    """Get input parameters from request.

    :param expecred_params: (array) Expected input
                            params specified in constants.
    """
    filters = {}
    for param in expected_params:
        value = pecan.request.GET.get(param)
        if value is not None:
            filters[param] = value
            LOG.debug('Parameter %(param)s has been received '
                      'with value %(value)s' % {
                          'param': param,
                          'value': value
                      })
    return filters


def parse_input_params(expected_input_params):
    """Parse input parameters from request.

    :param expected_input_params: (array) Expected input
                                  params specified in constants.
    """
    raw_filters = _get_input_params_from_request(expected_input_params)
    filters = copy.deepcopy(raw_filters)
    date_fmt = CONF.api.input_date_format

    for key, value in filters.items():
        if key == const.START_DATE or key == const.END_DATE:
            try:
                filters[key] = timeutils.parse_strtime(value, date_fmt)
            except (ValueError, TypeError) as exc:
                raise api_exc.ParseInputsError(
                    'Invalid date format: %(exc)s' % {'exc': exc})

    start_date = filters.get(const.START_DATE)
    end_date = filters.get(const.END_DATE)
    if start_date and end_date:
        if start_date > end_date:
            raise api_exc.ParseInputsError(
                'Invalid dates: %(start)s more than %(end)s'
                '' % {'start': const.START_DATE, 'end': const.END_DATE})
    if const.SIGNED in filters:
        if is_authenticated():
            filters[const.OPENID] = get_user_id()
        else:
            raise api_exc.ParseInputsError(
                'To see signed test results you need to authenticate')
    return filters


def str_to_bool(param):
    """Check if a string value should be evaluated as True or False."""
    if isinstance(param, bool):
        return param
    return param.lower() in ("true", "yes", "1")


def _calculate_pages_number(per_page, records_count):
    """Return pages number.

    :param per_page: (int) results number fot one page.
    :param records_count: (int) total records count.
    """
    quotient, remainder = divmod(records_count, per_page)
    if remainder > 0:
        return quotient + 1
    return quotient


def get_page_number(records_count):
    """Get page number from request.

    :param records_count: (int) total records count.
    """
    page_number = pecan.request.GET.get(const.PAGE)
    per_page = CONF.api.results_per_page

    total_pages = _calculate_pages_number(per_page, records_count)
    # The first page exists in any case
    if page_number is None:
        return (1, total_pages)
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        raise api_exc.ParseInputsError(
            'Invalid page number: The page number can not be converted to '
            'an integer')

    if page_number == 1:
        return (page_number, total_pages)

    if page_number <= 0:
        raise api_exc.ParseInputsError('Invalid page number: '
                                       'The page number less or equal zero.')

    if page_number > total_pages:
        raise api_exc.ParseInputsError(
            'Invalid page number: '
            'The page number is greater than the total number of pages.')

    return (page_number, total_pages)


def set_query_params(url, params):
    """Set params in given query."""
    url_parts = parse.urlparse(url)
    url = parse.urlunparse((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        url_parts.params,
        parse.urlencode(params),
        url_parts.fragment))
    return url


def get_token(length=30):
    """Get random token."""
    return ''.join(random.choice(string.ascii_lowercase)
                   for i in range(length))


def delete_params_from_user_session(params):
    """Delete params from user session."""
    session = get_user_session()
    for param in params:
        if session.get(param):
            del session[param]
    session.save()


def get_user_session():
    """Return user session."""
    return pecan.request.environ['beaker.session']


def get_token_data():
    """Return dict with data encoded from token."""
    return pecan.request.environ.get(const.JWT_TOKEN_ENV)


def get_user_id(from_session=True, from_token=True):
    """Return authenticated user id."""
    session = get_user_session()
    token = get_token_data()
    if from_session and session.get(const.USER_OPENID):
        return session.get(const.USER_OPENID)
    elif from_token and token:
        return token.get(const.USER_OPENID)


def get_user(user_id=None):
    """Return db record for authenticated user."""
    if not user_id:
        user_id = get_user_id()
    return db.user_get(user_id)


def get_user_public_keys():
    """Return public keys for authenticated user."""
    return db.get_user_pubkeys(get_user_id())


def is_authenticated(by_session=True, by_token=True):
    """Return True if user is authenticated."""
    user_id = get_user_id(from_session=by_session, from_token=by_token)
    if user_id:
        try:
            if get_user(user_id=user_id):
                return True
        except db.NotFound:
            pass
    return False


def enforce_permissions(test_id, level):
    """Check that user role is required for specified test run."""
    role = get_user_role(test_id)
    if not role:
        pecan.abort(401)

    if level == const.ROLE_USER:
        if role in (const.ROLE_OWNER, const.ROLE_USER, const.ROLE_FOUNDATION):
            return
        pecan.abort(403)
    elif level == const.ROLE_OWNER:
        if role in (const.ROLE_OWNER, const.ROLE_FOUNDATION):
            return
        pecan.abort(403)
    elif level == const.ROLE_FOUNDATION:
        if role in (const.ROLE_FOUNDATION):
            return
    else:
        raise ValueError('Permission level %s is undefined' % level)


def get_user_role(test_id):
    """Return user role for current user and specified test run."""
    if check_user_is_foundation_admin():
        return const.ROLE_FOUNDATION
    if check_owner(test_id):
        return const.ROLE_OWNER
    if check_user(test_id):
        return const.ROLE_USER
    return


def check_user(test_id):
    """Check that user has access to shared test run."""
    test_owner = db.get_test_meta_key(test_id, const.USER)
    if not test_owner:
        return True
    elif db.get_test_meta_key(test_id, const.SHARED_TEST_RUN):
        return True
    else:
        return check_owner(test_id)


def check_owner(test_id):
    """Check that user has access to specified test run as owner."""
    if not is_authenticated():
        return False

    test = db.get_test(test_id)
    # If the test is owned by a product.
    if test.get('product_version_id'):
        version = db.get_product_version(test['product_version_id'])
        return check_user_is_product_admin(version['product_id'])
    # Otherwise, check the user ownership.
    else:
        user = db.get_test_meta_key(test_id, const.USER)
        return user and user == get_user_id()


def check_permissions(level):
    """Decorator for checking permissions.

    It checks that user have enough permissions to access and manipulate
    an information about selected test run.
    Any user has role: const.ROLE_USER. It allows access to unsigned, shared
    and own test runs.
    Owner role: const.ROLE_OWNER allows access only to user's own results.
    """
    def decorator(method_or_class):

        def wrapper(method):
            @functools.wraps(method)
            def wrapped(*args, **kwargs):
                test_id = args[1]
                enforce_permissions(test_id, level)
                return method(*args, **kwargs)
            return wrapped

        if isinstance(method_or_class, types.FunctionType):
            return wrapper(method_or_class)
        elif issubclass(method_or_class, pecan.rest.RestController):
            controller = method_or_class
            for method_name in ('get', 'get_all', 'get_one',
                                'post', 'put', 'delete'):
                if hasattr(controller, method_name):
                    setattr(controller, method_name,
                            wrapper(getattr(controller, method_name)))
            return controller

    return decorator


def verify_openid_request(request):
    """Verify OpenID returned request in OpenID."""
    verify_params = dict(request.params.copy())
    verify_params["openid.mode"] = "check_authentication"

    verify_response = requests.post(
        CONF.osid.openstack_openid_endpoint, data=verify_params,
        verify=not CONF.api.app_dev_mode
    )
    verify_data_tokens = verify_response.content.split()
    verify_dict = dict((token.split(":")[0], token.split(":")[1])
                       for token in verify_data_tokens)

    if (verify_response.status_code / 100 != 2
            or verify_dict['is_valid'] != 'true'):
        pecan.abort(401, 'Authentication is failed. Try again.')

    # Is the data we've received within our required parameters?
    required_parameters = {
        const.OPENID_NS_SREG_EMAIL: 'Please permit access to '
                                    'your email address.',
        const.OPENID_NS_SREG_FULLNAME: 'Please permit access to '
                                       'your name.',
    }

    for name, error in six.iteritems(required_parameters):
        if name not in verify_params or not verify_params[name]:
            pecan.abort(401, 'Authentication is failed. %s' % error)

    return True


def check_user_is_foundation_admin(user_id=None):
    """Check is user in foundation group or not."""
    user = user_id if user_id else get_user_id()
    org_users = db.get_foundation_users()
    return user in org_users


def check_user_is_vendor_admin(vendor_id, user_id=None):
    """Check is user in vendor group or not."""
    user = user_id if user_id else get_user_id()
    org_users = db.get_organization_users(vendor_id)
    return user in org_users


def check_user_is_product_admin(product_id, user_id=None):
    """Check if the current user is in the vendor group for a product."""
    product = db.get_product(product_id)
    vendor_id = product['organization_id']
    return check_user_is_vendor_admin(vendor_id, user_id=user_id)


def decode_token(request):
    """Validate request signature.

    ValidationError rises if request is not valid.
    """
    if not request.headers.get(const.JWT_TOKEN_HEADER):
        return
    try:
        auth_schema, token = request.headers.get(
            const.JWT_TOKEN_HEADER).split(' ', 1)
    except ValueError:
        raise api_exc.ValidationError("Token is not valid")
    if auth_schema != 'Bearer':
        raise api_exc.ValidationError(
            "Authorization schema 'Bearer' should be used")
    try:
        token_data = jwt.decode(token, algorithms='RS256', verify=False)
    except jwt.InvalidTokenError:
        raise api_exc.ValidationError("Token is not valid")

    openid = token_data.get(const.USER_OPENID)
    if not openid:
        raise api_exc.ValidationError("Token does not contain user's openid")
    pubkeys = db.get_user_pubkeys(openid)
    for pubkey in pubkeys:
        try:
            pubkey_string = '%s %s' % (pubkey['format'], pubkey['pubkey'])
            pubkey_obj = serialization.load_ssh_public_key(
                pubkey_string.encode('utf-8'),
                backend=backends.default_backend()
            )
            pem_pubkey = pubkey_obj.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo)
        except (ValueError, IndexError, TypeError, binascii.Error):
            pass
        else:
            try:
                token_data = jwt.decode(
                    token, key=pem_pubkey,
                    options={'verify_signature': True,
                             'verify_exp': True,
                             'require_exp': True},
                    leeway=const.JWT_VALIDATION_LEEWAY)
                # NOTE(sslipushenko) If at least one key is valid, let
                # the validation pass
                return token_data
            except jwt.InvalidTokenError:
                pass

    # NOTE(sslipushenko) If all user's keys are not valid, the validation fails
    raise api_exc.ValidationError("Token is not valid")
