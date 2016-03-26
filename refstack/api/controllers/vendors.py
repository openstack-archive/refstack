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

"""Vendors controller."""

import base64
import six

from oslo_config import cfg
from oslo_log import log
import pecan
from pecan import rest
from pecan.secure import secure

from refstack.api import utils as api_utils
from refstack import db

LOG = log.getLogger(__name__)

CONF = cfg.CONF


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


class VendorsController(rest.RestController):
    """/v1/vendors handler."""

    users = UsersController()
