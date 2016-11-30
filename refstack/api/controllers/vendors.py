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

"""Vendors controller."""

import base64
import json
import six

from oslo_config import cfg
from oslo_db.exception import DBReferenceError
from oslo_log import log
import pecan
from pecan import rest
from pecan.secure import secure

from refstack.api import constants as const
from refstack.api.controllers import validation
from refstack.api import exceptions as api_exc
from refstack.api import utils as api_utils
from refstack.api import validators
from refstack import db

LOG = log.getLogger(__name__)

CONF = cfg.CONF


def _check_is_not_foundation(vendor_id):
    vendor = db.get_organization(vendor_id)
    if vendor['type'] == const.FOUNDATION:
        pecan.abort(403, 'Forbidden.')


class UsersController(rest.RestController):
    """/v1/vendors/<vendor_id>/users handler."""

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def get(self, vendor_id):
        """Return list of users in the vendor's group."""
        if not (api_utils.check_user_is_foundation_admin()
                or api_utils.check_user_is_vendor_admin(vendor_id)):
            return None

        org_users = db.get_organization_users(vendor_id)
        return [x for x in six.itervalues(org_users)]

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def put(self, vendor_id, openid):
        """Add user to vendor group."""
        openid = base64.b64decode(openid)

        if not (api_utils.check_user_is_foundation_admin()
                or api_utils.check_user_is_vendor_admin(vendor_id)):
            pecan.abort(403, 'Forbidden.')

        vendor = db.get_organization(vendor_id)
        creator = api_utils.get_user_id()
        db.add_user_to_group(openid, vendor['group_id'], creator)
        pecan.response.status = 204

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def delete(self, vendor_id, openid):
        """Remove user from vendor group."""
        openid = base64.b64decode(openid)

        if not (api_utils.check_user_is_foundation_admin()
                or api_utils.check_user_is_vendor_admin(vendor_id)):
            pecan.abort(403, 'Forbidden.')

        vendor = db.get_organization(vendor_id)
        db.remove_user_from_group(openid, vendor['group_id'])
        pecan.response.status = 204


class VendorsController(validation.BaseRestControllerWithValidation):
    """/v1/vendors handler."""

    users = UsersController()

    __validator__ = validators.VendorValidator

    _custom_actions = {
        "action": ["POST"],
    }

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def post(self):
        """'secure' decorator doesn't work at store_item. it must be here."""
        return super(VendorsController, self).post()

    @pecan.expose('json')
    def store_item(self, vendor):
        """Handler for create item. Should return new item id."""
        creator = api_utils.get_user_id()
        vendor = db.add_organization(vendor, creator)
        return {'id': vendor['id']}

    @secure(api_utils.is_authenticated)
    @pecan.expose('json', method='PUT')
    def put(self, vendor_id, **kw):
        """Handler for update item. Should return full info with updates."""
        is_foundation_admin = api_utils.check_user_is_foundation_admin()
        is_admin = (is_foundation_admin
                    or api_utils.check_user_is_vendor_admin(vendor_id))
        if not is_admin:
            pecan.abort(403, 'Forbidden.')
        vendor_info = {'id': vendor_id}
        vendor = db.get_organization(vendor_id)
        if 'name' in kw:
            if (vendor['type'] == const.OFFICIAL_VENDOR and
                    not is_foundation_admin):
                pecan.abort(
                    403, 'Name change for an official vendor is not allowed.')
            vendor_info['name'] = kw['name']
        if 'description' in kw:
            vendor_info['description'] = kw['description']
        if 'properties' in kw:
            vendor_info['properties'] = json.dumps(kw['properties'])
        vendor = db.update_organization(vendor_info)

        pecan.response.status = 200
        vendor['can_manage'] = True
        return vendor

    @pecan.expose('json')
    def get(self):
        """Get information of vendors."""
        allowed_keys = ['id', 'type', 'name', 'description']
        user = api_utils.get_user_id()
        try:
            is_admin = api_utils.check_user_is_foundation_admin()
            if is_admin:
                vendors = db.get_organizations(allowed_keys=allowed_keys)
                for vendor in vendors:
                    vendor['can_manage'] = True
            else:
                result = dict()
                types = [const.FOUNDATION, const.OFFICIAL_VENDOR]
                vendors = db.get_organizations_by_types(
                    types, allowed_keys=allowed_keys)
                for vendor in vendors:
                    _id = vendor['id']
                    result[_id] = vendor
                    result[_id]['can_manage'] = False

                vendors = db.get_organizations_by_user(
                    user, allowed_keys=allowed_keys)
                for vendor in vendors:
                    _id = vendor['id']
                    if _id not in result:
                        result[_id] = vendor
                    result[_id]['can_manage'] = True
                vendors = result.values()
        except Exception as ex:
            LOG.exception('An error occurred during '
                          'operation with database: %s' % ex)
            pecan.abort(400)

        return {'vendors': vendors}

    @pecan.expose('json')
    def get_one(self, vendor_id):
        """Get information about vendor."""
        allowed_keys = None
        is_admin = (api_utils.check_user_is_foundation_admin()
                    or api_utils.check_user_is_vendor_admin(vendor_id))
        if not is_admin:
            allowed_keys = ['id', 'type', 'name', 'description']

        vendor = db.get_organization(vendor_id, allowed_keys=allowed_keys)

        allowed_types = [const.FOUNDATION, const.OFFICIAL_VENDOR]
        if not is_admin and vendor['type'] not in allowed_types:
            pecan.abort(403, 'Forbidden.')

        vendor['can_manage'] = is_admin
        return vendor

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def delete(self, vendor_id):
        """Delete vendor."""
        if not (api_utils.check_user_is_foundation_admin()
                or api_utils.check_user_is_vendor_admin(vendor_id)):
            pecan.abort(403, 'Forbidden.')
        _check_is_not_foundation(vendor_id)

        try:
            db.delete_organization(vendor_id)
        except DBReferenceError:
            pecan.abort(400, 'Unable to delete. There are still tests '
                             'associated to products for this vendor.')
        pecan.response.status = 204

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def action(self, vendor_id, **kw):
        """Handler for action on Vendor object."""
        params = list()
        for param in ('register', 'approve', 'deny', 'cancel'):
            if param in kw:
                params.append(param)
        if len(params) != 1:
            raise api_exc.ValidationError(
                'Invalid actions in the body: ' + str(params))

        vendor = db.get_organization(vendor_id)
        if 'register' in params:
            self.register(vendor)
        elif 'approve' in params:
            self.approve(vendor)
        elif 'cancel' in params:
            self.cancel(vendor)
        else:
            self.deny(vendor, kw.get('registration_decline_reason'))

    def register(self, vendor):
        """Handler for applying for registration with Foundation."""
        if not api_utils.check_user_is_vendor_admin(vendor['id']):
            pecan.abort(403, 'Forbidden.')
        _check_is_not_foundation(vendor['id'])

        if vendor['type'] != const.PRIVATE_VENDOR:
            raise api_exc.ValidationError(
                'Invalid organization state for this action.')

        # change vendor type to pending
        org_info = {
            'id': vendor['id'],
            'type': const.PENDING_VENDOR}
        db.update_organization(org_info)

    def approve(self, vendor):
        """Handler for making vendor official."""
        if not api_utils.check_user_is_foundation_admin():
            pecan.abort(403, 'Forbidden.')
        _check_is_not_foundation(vendor['id'])

        if vendor['type'] != const.PENDING_VENDOR:
            raise api_exc.ValidationError(
                'Invalid organization state for this action.')

        # change vendor type to public
        props = vendor.get('properties')
        props = json.loads(props) if props else {}
        props.pop('registration_decline_reason', None)
        org_info = {
            'id': vendor['id'],
            'type': const.OFFICIAL_VENDOR,
            'properties': json.dumps(props)}
        db.update_organization(org_info)

    def cancel(self, vendor):
        """Handler for canceling registration.

        This action available to user. It allows him to cancel
        registrationand move state of his vendor from pending
        to private.
        """
        if not api_utils.check_user_is_vendor_admin(vendor['id']):
            pecan.abort(403, 'Forbidden.')
        _check_is_not_foundation(vendor['id'])

        if vendor['type'] != const.PENDING_VENDOR:
            raise api_exc.ValidationError(
                'Invalid organization state for this action.')

        # change vendor type back to private
        org_info = {
            'id': vendor['id'],
            'type': const.PRIVATE_VENDOR}
        db.update_organization(org_info)

    def deny(self, vendor, reason):
        """Handler for denying a vendor."""
        if not api_utils.check_user_is_foundation_admin():
            pecan.abort(403, 'Forbidden.')
        _check_is_not_foundation(vendor['id'])

        if not reason:
            raise api_exc.ValidationError(
                'The decline reason can not be empty')
        if vendor['type'] != const.PENDING_VENDOR:
            raise api_exc.ValidationError(
                'Invalid organization state for this action.')

        props = vendor.get('properties')
        props = json.loads(props) if props else {}
        props['registration_decline_reason'] = reason

        # change vendor type back to private
        org_info = {
            'id': vendor['id'],
            'type': const.PRIVATE_VENDOR,
            'properties': json.dumps(props)}
        db.update_organization(org_info)
