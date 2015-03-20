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

import mock
from oslo_config import fixture as config_fixture
from oslo_utils import timeutils
from oslotest import base

from refstack.api import constants as const
from refstack.api import utils as api_utils


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
        self.assertRaises(api_utils.ParseInputsError,
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
        self.assertRaises(api_utils.ParseInputsError,
                          api_utils.parse_input_params,
                          expected_params)

    @mock.patch.object(api_utils, '_get_input_params_from_request')
    def test_parse_input_params_success(self, mock_get_input):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.CONF.set_override('input_date_format',
                               fmt,
                               'api')
        raw_filters = {
            const.START_DATE: '2015-03-26 15:04:40',
            const.END_DATE: '2015-03-26 15:04:50',
            const.CPID: '12345',
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
            const.CPID: '12345'
        }

        result = api_utils.parse_input_params(expected_params)
        self.assertEqual(result, expected_result)

        mock_get_input.assert_called_once_with(expected_params)

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

        self.assertRaises(api_utils.ParseInputsError,
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

        self.assertRaises(api_utils.ParseInputsError,
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

        self.assertRaises(api_utils.ParseInputsError,
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
