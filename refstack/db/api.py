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

"""Defines interface for DB access.

Functions in this module are imported into the refstack.db namespace.
Call these functions from refstack.db namespace, not the refstack.db.api
namespace.
"""
from oslo_config import cfg
from oslo_db import api as db_api


db_opts = [
    cfg.StrOpt('db_backend',
               default='sqlalchemy',
               help='The backend to use for database.'),
]

CONF = cfg.CONF
CONF.register_opts(db_opts)

_BACKEND_MAPPING = {'sqlalchemy': 'refstack.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)

NotFound = IMPL.NotFound
Duplication = IMPL.Duplication


def store_results(results):
    """Storing results into database.

    :param results: Dict describes test results.
    """
    return IMPL.store_results(results)


def get_test(test_id, allowed_keys=None):
    """Get test run information from the database.

    :param test_id: The ID of the test.
    """
    return IMPL.get_test(test_id, allowed_keys=allowed_keys)


def delete_test(test_id):
    """Delete test run information from the database.

    :param test_id: The ID of the test.
    """
    return IMPL.delete_test(test_id)


def update_test(test_info):
    """Update test from the given test_info dictionary.

    :param test_info: The test
    """
    return IMPL.update_test(test_info)


def get_test_results(test_id):
    """Get all passed tempest tests for a specified test run.

    :param test_id: The ID of the test.
    """
    return IMPL.get_test_results(test_id)


def get_test_meta_key(test_id, key, default=None):
    """Get metadata value related to specified test run.

    :param test_id: The ID of the test.
    :param key: Metadata key
    :param default: Default value

    """
    return IMPL.get_test_meta_key(test_id, key, default)


def save_test_meta_item(test_id, key, value):
    """Store or update item value related to specified test run.

    :param test_id: The ID of the test.
    :param key: Metadata key

    """
    return IMPL.save_test_meta_item(test_id, key, value)


def delete_test_meta_item(test_id, key):
    """Delete metadata item related to specified test run.

    :param test_id: The ID of the test.
    :param key: Metadata key
    :param default: Default value

    :raise NotFound if default value is not set and no value found
    """
    return IMPL.delete_test_meta_item(test_id, key)


def get_test_records(page_number, per_page, filters):
    """Get page with applied filters for uploaded test records.

    :param page_number: The number of page.
    :param per_page: The number of results for one page.
    :param filters: (Dict) Filters that will be applied for records.
    """
    return IMPL.get_test_records(page_number, per_page, filters)


def get_test_records_count(filters):
    """Get total pages number with applied filters for uploaded test records.

    :param filters: (Dict) Filters that will be applied for records.
    """
    return IMPL.get_test_records_count(filters)


def user_get(user_openid):
    """Get user info.

    :param user_openid: User openid
    """
    return IMPL.user_get(user_openid)


def user_save(user_info):
    """Create user DB record if it exists, otherwise record will be updated.

    :param user_info: User record
    """
    return IMPL.user_save(user_info)


def get_pubkey(key):
    """Get pubkey info for a given key.

    :param key: public key
    """
    return IMPL.get_pubkey(key)


def store_pubkey(pubkey_info):
    """Store public key in to DB."""
    return IMPL.store_pubkey(pubkey_info)


def delete_pubkey(pubkey_id):
    """Delete public key from DB."""
    return IMPL.delete_pubkey(pubkey_id)


def get_user_pubkeys(user_openid):
    """Get public pubkeys for specified user."""
    return IMPL.get_user_pubkeys(user_openid)


def add_user_to_group(user_openid, group_id, created_by_user):
    """Add specified user to specified group."""
    return IMPL.add_user_to_group(user_openid, group_id, created_by_user)


def remove_user_from_group(user_openid, group_id):
    """Remove specified user from specified group."""
    return IMPL.remove_user_from_group(user_openid, group_id)


def add_organization(organization_info, creator):
    """Add organization."""
    return IMPL.add_organization(organization_info, creator)


def update_organization(organization_info):
    """Update organization."""
    return IMPL.update_organization(organization_info)


def get_organization(organization_id, allowed_keys=None):
    """Get organization by id."""
    return IMPL.get_organization(organization_id, allowed_keys=allowed_keys)


def delete_organization(organization_id):
    """delete organization by id."""
    return IMPL.delete_organization(organization_id)


def add_product(product_info, creator):
    """Add product from product_info dicionary with creator."""
    return IMPL.add_product(product_info, creator)


def update_product(product_info):
    """Update product from prodict_info dicionary."""
    return IMPL.update_product(product_info)


def get_product(id, allowed_keys=None):
    """Get product by id."""
    return IMPL.get_product(id, allowed_keys=allowed_keys)


def delete_product(id):
    """delete product by id."""
    return IMPL.delete_product(id)


def get_foundation_users():
    """Get users' openid-s that belong to group of foundation."""
    return IMPL.get_foundation_users()


def get_organization_users(organization_id):
    """Get users with info that belong to group of organization."""
    return IMPL.get_organization_users(organization_id)


def get_organizations(allowed_keys=None):
    """Get all organizations."""
    return IMPL.get_organizations(allowed_keys=allowed_keys)


def get_organizations_by_types(types, allowed_keys=None):
    """Get organization by list of types."""
    return IMPL.get_organizations_by_types(types, allowed_keys=allowed_keys)


def get_organizations_by_user(user_openid, allowed_keys=None):
    """Get organizations for specified user."""
    return IMPL.get_organizations_by_user(user_openid,
                                          allowed_keys=allowed_keys)


def get_products(allowed_keys=None, filters=None):
    """Get all products."""
    return IMPL.get_products(allowed_keys=allowed_keys, filters=filters)


def get_products_by_user(user_openid, allowed_keys=None, filters=None):
    """Get all products that user can manage."""
    return IMPL.get_products_by_user(user_openid, allowed_keys=allowed_keys,
                                     filters=filters)


def get_product_by_version(product_version_id, allowed_keys=None):
    """Get product info from a product version ID."""
    return IMPL.get_product_by_version(product_version_id,
                                       allowed_keys=allowed_keys)


def get_product_version(product_version_id, allowed_keys=None):
    """Get details of a specific version given the id."""
    return IMPL.get_product_version(product_version_id,
                                    allowed_keys=allowed_keys)


def get_product_version_by_cpid(cpid, allowed_keys=None):
    """Get a product version given a cloud provider id."""
    return IMPL.get_product_version_by_cpid(cpid, allowed_keys=allowed_keys)


def get_product_versions(product_id, allowed_keys=None):
    """Get all versions for a product."""
    return IMPL.get_product_versions(product_id, allowed_keys=allowed_keys)


def add_product_version(product_id, version, creator, cpid=None,
                        allowed_keys=None):
    """Add a new product version."""
    return IMPL.add_product_version(product_id, version, creator, cpid,
                                    allowed_keys=allowed_keys)


def update_product_version(product_version_info):
    """Update product version from product_info_version dictionary."""
    return IMPL.update_product_version(product_version_info)


def delete_product_version(product_version_id):
    """Delete a product version."""
    return IMPL.delete_product_version(product_version_id)
