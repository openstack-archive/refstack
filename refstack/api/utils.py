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
import copy
import random
import requests
import string

from oslo_config import cfg
from oslo_log import log
from oslo_utils import timeutils
import pecan
import six
from six.moves.urllib import parse

from refstack import db
from refstack.api import constants as const

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class ParseInputsError(Exception):

    """Raise if input params are invalid."""

    pass


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

    :param expecred_params: (array) Expected input
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
                raise ParseInputsError('Invalid date format: %(exc)s'
                                       % {'exc': exc})

    start_date = filters.get(const.START_DATE)
    end_date = filters.get(const.END_DATE)
    if start_date and end_date:
        if start_date > end_date:
            raise ParseInputsError('Invalid dates: %(start)s '
                                   'more than %(end)s' % {
                                       'start': const.START_DATE,
                                       'end': const.END_DATE
                                   })
    return filters


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
        raise ParseInputsError('Invalid page number: The page number can not '
                               'be converted to an integer')

    if page_number == 1:
        return (page_number, total_pages)

    if page_number <= 0:
        raise ParseInputsError('Invalid page number: '
                               'The page number less or equal zero.')

    if page_number > total_pages:
        raise ParseInputsError('Invalid page number: The page number '
                               'is greater than the total number of pages.')

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


def get_user_id():
    """Return authenticated user id."""
    return get_user_session().get(const.USER_OPENID)


def get_user():
    """Return db record for authenticated user."""
    return db.user_get(get_user_id())


def is_authenticated():
    """Return True if user is authenticated."""
    if get_user_id():
        try:
            if get_user():
                return True
        except db.UserNotFound:
            pass
    return False


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
