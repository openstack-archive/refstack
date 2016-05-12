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

from oslo_config import cfg
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

CONF = cfg.CONF


class ProductsController(validation.BaseRestControllerWithValidation):
    """/v1/products handler."""

    __validator__ = validators.ProductValidator

    _custom_actions = {
        "action": ["POST"],
    }

    @pecan.expose('json')
    def get(self):
        """Get information of all products."""
        allowed_keys = ['id', 'name', 'description', 'product_id', 'type',
                        'product_type', 'public', 'organization_id']
        user = api_utils.get_user_id()
        is_admin = user in db.get_foundation_users()
        try:
            if is_admin:
                products = db.get_products(allowed_keys=allowed_keys)
                for s in products:
                    s['can_manage'] = True
            else:
                result = dict()
                products = db.get_public_products(allowed_keys=allowed_keys)
                for s in products:
                    _id = s['id']
                    result[_id] = s
                    result[_id]['can_manage'] = False

                products = db.get_products_by_user(user,
                                                   allowed_keys=allowed_keys)
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
        product = db.get_product(id)
        vendor_id = product['organization_id']
        is_admin = (api_utils.check_user_is_foundation_admin() or
                    api_utils.check_user_is_vendor_admin(vendor_id))
        if not is_admin and not product['public']:
            pecan.abort(403, 'Forbidden.')

        if not is_admin:
            allowed_keys = ['id', 'name', 'description', 'product_id', 'type',
                            'product_type', 'public', 'organization_id']
            for key in product.keys():
                if key not in allowed_keys:
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
            product['product_id'] = six.text_type(uuid.uuid4())
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
        if 'product_id' in kw:
            product_info['product_id'] = kw['product_id']
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
        product = db.get_product(id)
        vendor_id = product['organization_id']
        if (not api_utils.check_user_is_foundation_admin() and
                not api_utils.check_user_is_vendor_admin(vendor_id)):
            pecan.abort(403, 'Forbidden.')

        db.delete_product(id)
        pecan.response.status = 204
