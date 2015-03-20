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

from oslo_config import cfg
from oslo_log import log
from oslo_utils import timeutils
import pecan

from refstack.api import constants as const

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class ParseInputsError(Exception):
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
    """Get page number from request
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
