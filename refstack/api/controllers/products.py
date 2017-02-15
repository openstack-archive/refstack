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

"""Product controller."""

import json
import uuid

from oslo_db.exception import DBReferenceError
from oslo_log import log
import pecan
from pecan.secure import secure
import six

from refstack.api import constants as const
from refstack.api.controllers import validation
from refstack.api import utils as api_utils
from refstack.api import validators
from refstack import db

LOG = log.getLogger(__name__)


class VersionsController(validation.BaseRestControllerWithValidation):
    """/v1/products/<product_id>/versions handler."""

    __validator__ = validators.ProductVersionValidator

    @pecan.expose('json')
    def get(self, id):
        """Get all versions for a product."""
        product = db.get_product(id)
        vendor_id = product['organization_id']
        is_admin = (api_utils.check_user_is_foundation_admin() or
                    api_utils.check_user_is_vendor_admin(vendor_id))
        if not product['public'] and not is_admin:
            pecan.abort(403, 'Forbidden.')

        allowed_keys = ['id', 'product_id', 'version', 'cpid']
        return db.get_product_versions(id, allowed_keys=allowed_keys)

    @pecan.expose('json')
    def get_one(self, id, version_id):
        """Get specific version information."""
        product = db.get_product(id)
        vendor_id = product['organization_id']
        is_admin = (api_utils.check_user_is_foundation_admin() or
                    api_utils.check_user_is_vendor_admin(vendor_id))
        if not product['public'] and not is_admin:
            pecan.abort(403, 'Forbidden.')
        allowed_keys = ['id', 'product_id', 'version', 'cpid']
        return db.get_product_version(version_id, allowed_keys=allowed_keys)

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def post(self, id):
        """'secure' decorator doesn't work at store_item. it must be here."""
        self.product_id = id
        return super(VersionsController, self).post()

    @pecan.expose('json')
    def store_item(self, version_info):
        """Add a new version for the product."""
        if (not api_utils.check_user_is_product_admin(self.product_id) and
                not api_utils.check_user_is_foundation_admin()):
            pecan.abort(403, 'Forbidden.')

        creator = api_utils.get_user_id()
        pecan.response.status = 201
        allowed_keys = ['id', 'product_id', 'version', 'cpid']
        return db.add_product_version(self.product_id, version_info['version'],
                                      creator, version_info.get('cpid'),
                                      allowed_keys)

    @secure(api_utils.is_authenticated)
    @pecan.expose('json', method='PUT')
    def put(self, id, version_id, **kw):
        """Update details for a specific version.

        Endpoint: /v1/products/<product_id>/versions/<version_id>
        """
        if (not api_utils.check_user_is_product_admin(id) and
                not api_utils.check_user_is_foundation_admin()):
            pecan.abort(403, 'Forbidden.')

        version_info = {'id': version_id}
        if 'cpid' in kw:
            version_info['cpid'] = kw['cpid']
        version = db.update_product_version(version_info)
        pecan.response.status = 200
        return version

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def delete(self, id, version_id):
        """Delete a product version.

        Endpoint: /v1/products/<product_id>/versions/<version_id>
        """
        if (not api_utils.check_user_is_product_admin(id) and
                not api_utils.check_user_is_foundation_admin()):

            pecan.abort(403, 'Forbidden.')
        try:
            version = db.get_product_version(version_id,
                                             allowed_keys=['version'])
            if not version['version']:
                pecan.abort(400, 'Can not delete the empty version as it is '
                                 'used for basic product/test association. '
                                 'This version was implicitly created with '
                                 'the product, and so it cannot be deleted '
                                 'explicitly.')

            db.delete_product_version(version_id)
        except DBReferenceError:
            pecan.abort(400, 'Unable to delete. There are still tests '
                             'associated to this product version.')
        pecan.response.status = 204


class ProductsController(validation.BaseRestControllerWithValidation):
    """/v1/products handler."""

    __validator__ = validators.ProductValidator

    _custom_actions = {
        "action": ["POST"],
    }

    versions = VersionsController()

    @pecan.expose('json')
    def get(self):
        """Get information of all products."""
        filters = api_utils.parse_input_params(['organization_id'])

        allowed_keys = ['id', 'name', 'description', 'product_ref_id', 'type',
                        'product_type', 'public', 'organization_id']
        user = api_utils.get_user_id()
        is_admin = user in db.get_foundation_users()
        try:
            if is_admin:
                products = db.get_products(allowed_keys=allowed_keys,
                                           filters=filters)
                for s in products:
                    s['can_manage'] = True
            else:
                result = dict()
                filters['public'] = True

                products = db.get_products(allowed_keys=allowed_keys,
                                           filters=filters)
                for s in products:
                    _id = s['id']
                    result[_id] = s
                    result[_id]['can_manage'] = False

                filters.pop('public')
                products = db.get_products_by_user(user,
                                                   allowed_keys=allowed_keys,
                                                   filters=filters)
                for s in products:
                    _id = s['id']
                    if _id not in result:
                        result[_id] = s
                    result[_id]['can_manage'] = True
                products = result.values()
        except Exception as ex:
            LOG.exception('An error occurred during '
                          'operation with database: %s' % ex)
            pecan.abort(400)

        products.sort(key=lambda x: x['name'])
        return {'products': products}

    @pecan.expose('json')
    def get_one(self, id):
        """Get information about product."""
        allowed_keys = ['id', 'name', 'description',
                        'product_ref_id', 'product_type',
                        'public', 'properties', 'created_at', 'updated_at',
                        'organization_id', 'created_by_user', 'type']
        product = db.get_product(id, allowed_keys=allowed_keys)
        vendor_id = product['organization_id']
        is_admin = (api_utils.check_user_is_foundation_admin() or
                    api_utils.check_user_is_vendor_admin(vendor_id))
        if not is_admin and not product['public']:
            pecan.abort(403, 'Forbidden.')
        if not is_admin:
            admin_only_keys = ['created_by_user', 'created_at', 'updated_at',
                               'properties']
            for key in product.keys():
                if key in admin_only_keys:
                    product.pop(key)

        product['can_manage'] = is_admin
        return product

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def post(self):
        """'secure' decorator doesn't work at store_item. it must be here."""
        return super(ProductsController, self).post()

    @pecan.expose('json')
    def store_item(self, product):
        """Handler for storing item. Should return new item id."""
        creator = api_utils.get_user_id()
        product['type'] = (const.SOFTWARE
                           if product['product_type'] == const.DISTRO
                           else const.CLOUD)
        if product['type'] == const.SOFTWARE:
            product['product_ref_id'] = six.text_type(uuid.uuid4())
        vendor_id = product.pop('organization_id', None)
        if not vendor_id:
            # find or create default vendor for new product
            # TODO(andrey-mp): maybe just fill with info here and create
            # at DB layer in one transaction
            default_vendor_name = 'vendor_' + creator
            vendors = db.get_organizations_by_user(creator)
            for v in vendors:
                if v['name'] == default_vendor_name:
                    vendor_id = v['id']
                    break
            else:
                vendor = {'name': default_vendor_name}
                vendor = db.add_organization(vendor, creator)
                vendor_id = vendor['id']
        product['organization_id'] = vendor_id
        product = db.add_product(product, creator)
        return {'id': product['id']}

    @secure(api_utils.is_authenticated)
    @pecan.expose('json', method='PUT')
    def put(self, id, **kw):
        """Handler for update item. Should return full info with updates."""
        product = db.get_product(id)
        vendor_id = product['organization_id']
        vendor = db.get_organization(vendor_id)
        is_admin = (api_utils.check_user_is_foundation_admin()
                    or api_utils.check_user_is_vendor_admin(vendor_id))
        if not is_admin:
            pecan.abort(403, 'Forbidden.')

        product_info = {'id': id}
        if 'name' in kw:
            product_info['name'] = kw['name']
        if 'description' in kw:
            product_info['description'] = kw['description']
        if 'product_ref_id' in kw:
            product_info['product_ref_id'] = kw['product_ref_id']
        if 'public' in kw:
            # user can mark product as public only if
            # his/her vendor is public(official)
            public = api_utils.str_to_bool(kw['public'])
            if (vendor['type'] not in (const.OFFICIAL_VENDOR, const.FOUNDATION)
                    and public):
                pecan.abort(403, 'Forbidden.')
            product_info['public'] = public
        if 'properties' in kw:
            product_info['properties'] = json.dumps(kw['properties'])
        db.update_product(product_info)

        pecan.response.status = 200
        product = db.get_product(id)
        product['can_manage'] = True
        return product

    @secure(api_utils.is_authenticated)
    @pecan.expose('json')
    def delete(self, id):
        """Delete product."""
        if (not api_utils.check_user_is_foundation_admin() and
                not api_utils.check_user_is_product_admin(id)):
            pecan.abort(403, 'Forbidden.')
        try:
            db.delete_product(id)
        except DBReferenceError:
            pecan.abort(400, 'Unable to delete. There are still tests '
                             'associated to versions of this product.')
        pecan.response.status = 204
