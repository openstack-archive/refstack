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
import functools

from oslo_config import cfg
from oslo_log import log
import pecan
from pecan import rest
import six
from six.moves.urllib import parse

from refstack import db
from refstack.api import constants as const
from refstack.api import utils as api_utils
from refstack.api import validators
from refstack.api.controllers import validation

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class MetadataController(rest.RestController):
    """/v1/results/<test_id>/meta handler."""

    rw_access_keys = ('shared', 'guideline', 'target',)

    def _check_key(func):
        """Decorator to check that a specific key has write access."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            meta_key = args[2]
            if meta_key not in args[0].rw_access_keys:
                pecan.abort(403)
            return func(*args, **kwargs)
        return wrapper

    @pecan.expose('json')
    def get(self, test_id):
        """Get test run metadata."""
        test_info = db.get_test(test_id)
        role = api_utils.get_user_role(test_id)
        if role in (const.ROLE_FOUNDATION, const.ROLE_OWNER):
            return test_info['meta']
        elif role in (const.ROLE_USER):
            return {k: v for k, v in six.iteritems(test_info['meta'])
                    if k in self.rw_access_keys}
        pecan.abort(403)

    @pecan.expose('json')
    def get_one(self, test_id, key):
        """Get value for key from test run metadata."""
        role = api_utils.get_user_role(test_id)
        if role in (const.ROLE_FOUNDATION, const.ROLE_OWNER):
            return db.get_test_meta_key(test_id, key)
        elif role in (const.ROLE_USER) and key in self.rw_access_keys:
            return db.get_test_meta_key(test_id, key)
        pecan.abort(403)

    @_check_key
    @api_utils.check_permissions(level=const.ROLE_OWNER)
    @pecan.expose('json')
    def post(self, test_id, key):
        """Save value for key in test run metadata."""
        test = db.get_test(test_id)
        if test['verification_status'] == const.TEST_VERIFIED:
            pecan.abort(403, 'Can not add/alter a new metadata key for a '
                             'verified test run.')
        db.save_test_meta_item(test_id, key, pecan.request.body)
        pecan.response.status = 201

    @_check_key
    @api_utils.check_permissions(level=const.ROLE_OWNER)
    @pecan.expose('json')
    def delete(self, test_id, key):
        """Delete key from test run metadata."""
        test = db.get_test(test_id)
        if test['verification_status'] == const.TEST_VERIFIED:
            pecan.abort(403, 'Can not delete a metadata key for a '
                             'verified test run.')
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
        user_role = api_utils.get_user_role(test_id)
        if user_role in (const.ROLE_FOUNDATION, const.ROLE_OWNER):
            test_info = db.get_test(
                test_id, allowed_keys=['id', 'cpid', 'created_at',
                                       'duration_seconds', 'meta',
                                       'product_version',
                                       'verification_status']
            )
        else:
            test_info = db.get_test(test_id)
        test_list = db.get_test_results(test_id)
        test_name_list = [test_dict['name'] for test_dict in test_list]
        test_info.update({'results': test_name_list,
                          'user_role': user_role})

        if user_role not in (const.ROLE_FOUNDATION, const.ROLE_OWNER):
            # Don't expose product information if product is not public.
            if (test_info.get('product_version') and
               not test_info['product_version']['product_info']['public']):

                test_info['product_version'] = None

            test_info['meta'] = {
                k: v for k, v in six.iteritems(test_info['meta'])
                if k in MetadataController.rw_access_keys
            }
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
            if test.get('cpid'):
                version = db.get_product_version_by_cpid(
                    test['cpid'], allowed_keys=['id', 'product_id'])
                # Only auto-associate if there is a single product version
                # with the given cpid.
                if len(version) == 1:
                    is_foundation = api_utils.check_user_is_foundation_admin(
                        pubkey.openid)
                    is_product_admin = api_utils.check_user_is_product_admin(
                        version[0]['product_id'], pubkey.openid)
                    if is_foundation or is_product_admin:
                        test_['product_version_id'] = version[0]['id']
        test_id = db.store_results(test_)
        return {'test_id': test_id,
                'url': parse.urljoin(CONF.ui_url,
                                     CONF.api.test_results_url) % test_id}

    @pecan.expose('json')
    @api_utils.check_permissions(level=const.ROLE_OWNER)
    def delete(self, test_id):
        """Delete test run."""
        test = db.get_test(test_id)
        if test['verification_status'] == const.TEST_VERIFIED:
            pecan.abort(403, 'Can not delete a verified test run.')

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
            const.SIGNED,
            const.VERIFICATION_STATUS,
            const.PRODUCT_ID
        ]

        filters = api_utils.parse_input_params(expected_input_params)

        if const.PRODUCT_ID in filters:
            product = db.get_product(filters[const.PRODUCT_ID])
            vendor_id = product['organization_id']
            is_admin = (api_utils.check_user_is_foundation_admin() or
                        api_utils.check_user_is_vendor_admin(vendor_id))
            if is_admin:
                filters[const.ALL_PRODUCT_TESTS] = True
            elif not product['public']:
                pecan.abort(403, 'Forbidden.')

        records_count = db.get_test_records_count(filters)
        page_number, total_pages_number = \
            api_utils.get_page_number(records_count)

        try:
            per_page = CONF.api.results_per_page
            results = db.get_test_records(page_number, per_page, filters)
            is_foundation = api_utils.check_user_is_foundation_admin()
            for result in results:

                if not (api_utils.check_owner(result['id']) or is_foundation):

                    # Don't expose product info if the product is not public.
                    if (result.get('product_version') and not
                       result['product_version']['product_info']['public']):

                        result['product_version'] = None
                    # Only show all metadata if the user is the owner or a
                    # member of the Foundation group.
                    result['meta'] = {
                        k: v for k, v in six.iteritems(result['meta'])
                        if k in MetadataController.rw_access_keys
                    }
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
                      'operation with database: %s' % str(ex))
            pecan.abort(500)

        return page

    @api_utils.check_permissions(level=const.ROLE_OWNER)
    @pecan.expose('json')
    def put(self, test_id, **kw):
        """Update a test result."""
        test_info = {'id': test_id}
        is_foundation_admin = api_utils.check_user_is_foundation_admin()

        if 'product_version_id' in kw:
            test = db.get_test(test_id)
            if test['verification_status'] == const.TEST_VERIFIED:
                pecan.abort(403, 'Can not update product_version_id for a '
                                 'verified test run.')

            if kw['product_version_id']:
                # Verify that the user is a member of the product's vendor.
                version = db.get_product_version(kw['product_version_id'],
                                                 allowed_keys=['product_id'])
                is_vendor_admin = (
                    api_utils
                    .check_user_is_product_admin(version['product_id'])
                )
            else:
                # No product vendor to check membership for, so just set
                # is_vendor_admin to True.
                is_vendor_admin = True
                kw['product_version_id'] = None

            if not is_vendor_admin and not is_foundation_admin:
                pecan.abort(403, 'Forbidden.')

            test_info['product_version_id'] = kw['product_version_id']

        if 'verification_status' in kw:
            if not is_foundation_admin:
                pecan.abort(403, 'You do not have permission to change a '
                                 'verification status.')

            if kw['verification_status'] not in (0, 1):
                pecan.abort(400, 'Invalid verification_status value: %d' %
                                 kw['verification_status'])

            # Check pre-conditions are met to mark a test verified.
            if (kw['verification_status'] == 1 and
                not (db.get_test_meta_key(test_id, 'target') and
                     db.get_test_meta_key(test_id, 'guideline') and
                     db.get_test_meta_key(test_id, const.SHARED_TEST_RUN))):

                pecan.abort(403, 'In order to mark a test verified, the '
                                 'test must be shared and have been '
                                 'associated to a guideline and target '
                                 'program.')

            test_info['verification_status'] = kw['verification_status']

        test = db.update_test(test_info)
        pecan.response.status = 201
        return test
