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

"""User profile controller."""

import pecan
from pecan import rest
from pecan.secure import secure

from refstack.api import utils as api_utils
from refstack.api import validators
from refstack.api.controllers import validation
from refstack import db


class PublicKeysController(validation.BaseRestControllerWithValidation):
    """/v1/profile/pubkeys handler."""

    __validator__ = validators.PubkeyValidator

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def post(self, ):
        """Handler for uploading public pubkeys."""
        return super(PublicKeysController, self).post()

    def store_item(self, body):
        """Handler for storing item."""
        pubkey = {'openid': api_utils.get_user_id()}
        parts = body['raw_key'].strip().split()
        if len(parts) == 2:
            parts.append('')
        pubkey['format'], pubkey['pubkey'], pubkey['comment'] = parts
        pubkey_id = db.store_pubkey(pubkey)
        return pubkey_id

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def get(self):
        """Retrieve all user's public pubkeys."""
        return api_utils.get_user_public_keys()

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def delete(self, pubkey_id):
        """Delete public key."""
        pubkeys = api_utils.get_user_public_keys()
        for key in pubkeys:
            if key['id'] == pubkey_id:
                db.delete_pubkey(pubkey_id)
                pecan.response.status = 204
                return
        else:
            pecan.abort(404)


class ProfileController(rest.RestController):
    """Controller provides user information in OpenID 2.0 IdP.

    /v1/profile handler
    """

    pubkeys = PublicKeysController()

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def get(self):
        """Handle get request on user info."""
        user = api_utils.get_user()
        return {
            "openid": user.openid,
            "email": user.email,
            "fullname": user.fullname,
            "is_admin": api_utils.check_user_is_foundation_admin()
        }
