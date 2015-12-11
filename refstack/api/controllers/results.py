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

"""Test results controller."""

from oslo_config import cfg
from oslo_log import log
import pecan
from pecan import rest
from six.moves.urllib import parse

from refstack import db
from refstack.api import constants as const
from refstack.api import utils as api_utils
from refstack.api import validators
from refstack.api.controllers import validation

LOG = log.getLogger(__name__)

CONF = cfg.CONF


@api_utils.check_permissions(level=const.ROLE_USER)
class MetadataController(rest.RestController):
    """/v1/results/<test_id>/meta handler."""

    rw_access_keys = ('shared', 'guideline', 'target',)

    @pecan.expose('json')
    def get(self, test_id):
        """Get test run metadata."""
        test_info = db.get_test(test_id)
        return test_info['meta']

    @pecan.expose('json')
    def get_one(self, test_id, key):
        """Get value for key from test run metadata."""
        return db.get_test_meta_key(test_id, key)

    @api_utils.check_permissions(level=const.ROLE_OWNER)
    @pecan.expose('json')
    def post(self, test_id, key):
        """Save value for key in test run metadata."""
        db.save_test_meta_item(test_id, key, pecan.request.body)
        pecan.response.status = 201

    @api_utils.check_permissions(level=const.ROLE_OWNER)
    @pecan.expose('json')
    def delete(self, test_id, key):
        """Delete key from test run metadata."""
        db.delete_test_meta_item(test_id, key)
        pecan.response.status = 204


class ResultsController(validation.BaseRestControllerWithValidation):
    """/v1/results handler."""

    __validator__ = validators.TestResultValidator

    meta = MetadataController()

    @pecan.expose('json')
    @api_utils.check_permissions(level=const.ROLE_USER)
    def get_one(self, test_id):
        """Handler for getting item."""
        if api_utils.get_user_role(test_id) == const.ROLE_OWNER:
            test_info = db.get_test(
                test_id, allowed_keys=['id', 'cpid', 'created_at',
                                       'duration_seconds', 'meta']
            )
        else:
            test_info = db.get_test(test_id)
        test_list = db.get_test_results(test_id)
        test_name_list = [test_dict['name'] for test_dict in test_list]
        test_info.update({'results': test_name_list,
                          'user_role': api_utils.get_user_role(test_id)})
        return test_info

    def store_item(self, test):
        """Handler for storing item. Should return new item id."""
        test_ = test.copy()
        if pecan.request.headers.get('X-Public-Key'):
            key = pecan.request.headers.get('X-Public-Key').strip().split()[1]
            if 'meta' not in test_:
                test_['meta'] = {}
            pubkey = db.get_pubkey(key)
            if not pubkey:
                pecan.abort(400, 'User with specified key not found. '
                                 'Please log into the RefStack server to '
                                 'upload your key.')

            test_['meta'][const.USER] = pubkey.openid
        test_id = db.store_results(test_)
        return {'test_id': test_id,
                'url': parse.urljoin(CONF.ui_url,
                                     CONF.api.test_results_url) % test_id}

    @pecan.expose('json')
    @api_utils.check_permissions(level=const.ROLE_OWNER)
    def delete(self, test_id):
        """Delete test run."""
        db.delete_test(test_id)
        pecan.response.status = 204

    @pecan.expose('json')
    def get(self):
        """Get information of all uploaded test results.

        Get information of all uploaded test results in descending
        chronological order. Make it possible to specify some
        input parameters for filtering.
        For example:
            /v1/results?page=<page number>&cpid=1234.
        By default, page is set to page number 1,
        if the page parameter is not specified.
        """
        expected_input_params = [
            const.START_DATE,
            const.END_DATE,
            const.CPID,
            const.SIGNED
        ]

        filters = api_utils.parse_input_params(expected_input_params)
        records_count = db.get_test_records_count(filters)
        page_number, total_pages_number = \
            api_utils.get_page_number(records_count)

        try:
            per_page = CONF.api.results_per_page
            results = db.get_test_records(page_number, per_page, filters)

            for result in results:
                result.update({'url': parse.urljoin(
                    CONF.ui_url, CONF.api.test_results_url
                ) % result['id']})

            page = {'results': results,
                    'pagination': {
                        'current_page': page_number,
                        'total_pages': total_pages_number
                    }}
        except Exception as ex:
            LOG.debug('An error occurred during '
                      'operation with database: %s' % ex)
            pecan.abort(400)

        return page
