# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

"""Implementation of SQLAlchemy backend."""

import base64
import hashlib
import sys
import uuid

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session as db_session
from oslo_log import log
import six

from refstack.api import constants as api_const
from refstack.db.sqlalchemy import models


CONF = cfg.CONF

_FACADE = None
LOG = log.getLogger(__name__)

db_options.set_defaults(cfg.CONF)


class NotFound(Exception):
    """Raise if item not found in db."""

    pass


class Duplication(Exception):
    """Raise if unique constraint violates."""

    pass


def _create_facade_lazily():
    """Create DB facade lazily."""
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    """Get DB engine."""
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    """Get DB session."""
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def _to_dict(sqlalchemy_object, allowed_keys=None):
    if isinstance(sqlalchemy_object, list):
        return [_to_dict(obj, allowed_keys=allowed_keys)
                for obj in sqlalchemy_object]
    if (hasattr(sqlalchemy_object, 'keys')
            and hasattr(sqlalchemy_object, 'index')):
        return {key: getattr(sqlalchemy_object, key)
                for key in sqlalchemy_object.keys()}
    if hasattr(sqlalchemy_object, 'default_allowed_keys'):
        items = sqlalchemy_object.iteritems()
        if not allowed_keys:
            allowed_keys = sqlalchemy_object.default_allowed_keys
        if allowed_keys:
            items = filter(lambda item: item[0] in allowed_keys, items)
        result = {}
        for key, value in items:
            if key in sqlalchemy_object.metadata_keys:
                result[key] = {
                    item.get(sqlalchemy_object.metadata_keys[key]['key']):
                    item.get(sqlalchemy_object.metadata_keys[key]['value'])
                    for item in value}
            elif hasattr(value, 'default_allowed_keys'):
                result[key] = _to_dict(value)
            elif (isinstance(value, list) and value
                  and hasattr(value[0], 'default_allowed_keys')):
                result[key] = [_to_dict(item) for item in value]
            else:
                result[key] = value
        return result
    if hasattr(sqlalchemy_object, 'all'):
        return _to_dict(sqlalchemy_object.all())
    return sqlalchemy_object


def store_results(results):
    """Store test results."""
    test = models.Test()
    test_id = str(uuid.uuid4())
    test.id = test_id
    test.cpid = results.get('cpid')
    test.duration_seconds = results.get('duration_seconds')
    test.product_version_id = results.get('product_version_id')
    session = get_session()
    with session.begin():
        for result in results.get('results', []):
            test_result = models.TestResults()
            test_result.test_id = test_id
            test_result.name = result['name']
            test_result.uuid = result.get('uuid', None)
            test.results.append(test_result)
        for k, v in six.iteritems(results.get('meta', {})):
            meta = models.TestMeta()
            meta.meta_key, meta.value = k, v
            test.meta.append(meta)
        test.save(session)
    return test_id


def get_test(test_id, allowed_keys=None):
    """Get test info."""
    session = get_session()
    test_info = session.query(models.Test). \
        filter_by(id=test_id). \
        first()
    if not test_info:
        raise NotFound('Test result %s not found' % test_id)
    return _to_dict(test_info, allowed_keys)


def delete_test(test_id):
    """Delete test information from the database."""
    session = get_session()
    with session.begin():
        test = session.query(models.Test).filter_by(id=test_id).first()
        if test:
            session.query(models.TestMeta) \
                .filter_by(test_id=test_id).delete()
            session.query(models.TestResults) \
                .filter_by(test_id=test_id).delete()
            session.delete(test)
        else:
            raise NotFound('Test result %s not found' % test_id)


def update_test(test_info):
    """Update test from the given test_info dictionary."""
    session = get_session()
    _id = test_info.get('id')
    test = session.query(models.Test).filter_by(id=_id).first()
    if test is None:
        raise NotFound('Test result with id %s not found' % _id)

    keys = ['product_version_id', 'verification_status']
    for key in keys:
        if key in test_info:
            setattr(test, key, test_info[key])

    with session.begin():
        test.save(session=session)
        return _to_dict(test)


def get_test_meta_key(test_id, key, default=None):
    """Get metadata value related to specified test run."""
    session = get_session()
    meta_item = session.query(models.TestMeta). \
        filter_by(test_id=test_id). \
        filter_by(meta_key=key). \
        first()
    value = meta_item.value if meta_item else default
    return value


def save_test_meta_item(test_id, key, value):
    """Store or update item value related to specified test run."""
    session = get_session()
    meta_item = (session.query(models.TestMeta)
                 .filter_by(test_id=test_id)
                 .filter_by(meta_key=key).first() or models.TestMeta())
    meta_item.test_id = test_id
    meta_item.meta_key = key
    meta_item.value = value
    with session.begin():
        meta_item.save(session)


def delete_test_meta_item(test_id, key):
    """Delete metadata item related to specified test run."""
    session = get_session()
    meta_item = session.query(models.TestMeta). \
        filter_by(test_id=test_id). \
        filter_by(meta_key=key). \
        first()
    if meta_item:
        with session.begin():
            session.delete(meta_item)
    else:
        raise NotFound('Metadata key %s '
                       'not found for test run %s' % (key, test_id))


def get_test_results(test_id):
    """Get test results."""
    session = get_session()
    results = session.query(models.TestResults). \
        filter_by(test_id=test_id). \
        all()
    return [_to_dict(result) for result in results]


def _apply_filters_for_query(query, filters):
    """Apply filters for DB query."""
    start_date = filters.get(api_const.START_DATE)
    if start_date:
        query = query.filter(models.Test.created_at >= start_date)

    end_date = filters.get(api_const.END_DATE)
    if end_date:
        query = query.filter(models.Test.created_at <= end_date)

    cpid = filters.get(api_const.CPID)
    if cpid:
        query = query.filter(models.Test.cpid == cpid)

    verification_status = filters.get(api_const.VERIFICATION_STATUS)
    if verification_status:
        query = query.filter(models.Test.verification_status ==
                             verification_status)

    if api_const.PRODUCT_ID in filters:
        query = (query
                 .join(models.ProductVersion)
                 .filter(models.ProductVersion.product_id ==
                         filters[api_const.PRODUCT_ID]))

    all_product_tests = filters.get(api_const.ALL_PRODUCT_TESTS)
    signed = api_const.SIGNED in filters
    # If we only want to get the user's test results.
    if signed:
        query = (query
                 .join(models.Test.meta)
                 .filter(models.TestMeta.meta_key == api_const.USER)
                 .filter(models.TestMeta.value == filters[api_const.OPENID])
                 )
    elif not all_product_tests:
        # Get all non-signed (aka anonymously uploaded) test results
        # along with signed but shared test results.
        signed_results = (query.session
                          .query(models.TestMeta.test_id)
                          .filter_by(meta_key=api_const.USER))
        shared_results = (query.session
                          .query(models.TestMeta.test_id)
                          .filter_by(meta_key=api_const.SHARED_TEST_RUN))
        query = (query.filter(models.Test.id.notin_(signed_results))
                 .union(query.filter(models.Test.id.in_(shared_results))))

    return query


def get_test_records(page, per_page, filters):
    """Get page with list of test records."""
    session = get_session()
    query = session.query(models.Test)
    query = _apply_filters_for_query(query, filters)
    results = query.order_by(models.Test.created_at.desc()). \
        offset(per_page * (page - 1)). \
        limit(per_page).all()
    return _to_dict(results)


def get_test_records_count(filters):
    """Get total test records count."""
    session = get_session()
    query = session.query(models.Test.id)
    records_count = _apply_filters_for_query(query, filters).count()

    return records_count


def user_get(user_openid):
    """Get user info by openid."""
    session = get_session()
    user = session.query(models.User).filter_by(openid=user_openid).first()
    if user is None:
        raise NotFound('User with OpenID %s not found' % user_openid)
    return user


def user_save(user_info):
    """Create user DB record if it exists, otherwise record will be updated."""
    try:
        user = user_get(user_info['openid'])
    except NotFound:
        user = models.User()

    session = get_session()
    with session.begin():
        user.update(user_info)
        user.save(session=session)
        return user


def get_pubkey(key):
    """Get the pubkey info corresponding to the given public key.

    The md5 hash of the key is used for the query for quicker lookups.
    """
    session = get_session()
    md5_hash = hashlib.md5(base64.b64decode(key.encode('ascii'))).hexdigest()
    pubkeys = session.query(models.PubKey).filter_by(md5_hash=md5_hash).all()
    if len(pubkeys) == 1:
        return pubkeys[0]
    elif len(pubkeys) > 1:
        for pubkey in pubkeys:
            if pubkey['pubkey'] == key:
                return pubkey
    return None


def store_pubkey(pubkey_info):
    """Store public key in to DB."""
    pubkey = models.PubKey()
    pubkey.openid = pubkey_info['openid']
    pubkey.format = pubkey_info['format']
    pubkey.pubkey = pubkey_info['pubkey']
    pubkey.md5_hash = hashlib.md5(
        base64.b64decode(
            pubkey_info['pubkey'].encode('ascii')
        )
    ).hexdigest()
    pubkey.comment = pubkey_info['comment']
    session = get_session()
    with session.begin():
        pubkeys_collision = (session.
                             query(models.PubKey).
                             filter_by(md5_hash=pubkey.md5_hash).
                             filter_by(pubkey=pubkey.pubkey).all())
        if not pubkeys_collision:
            pubkey.save(session)
        else:
            raise Duplication('Public key already exists.')
    return pubkey.id


def delete_pubkey(id):
    """Delete public key from DB."""
    session = get_session()
    with session.begin():
        key = session.query(models.PubKey).filter_by(id=id).first()
        session.delete(key)


def get_user_pubkeys(user_openid):
    """Get public pubkeys for specified user."""
    session = get_session()
    pubkeys = session.query(models.PubKey).filter_by(openid=user_openid).all()
    return _to_dict(pubkeys)


def add_user_to_group(user_openid, group_id, created_by_user):
    """Add specified user to specified group."""
    item = models.UserToGroup()
    session = get_session()
    with session.begin():
        item.user_openid = user_openid
        item.group_id = group_id
        item.created_by_user = created_by_user
        item.save(session=session)


def remove_user_from_group(user_openid, group_id):
    """Remove specified user from specified group."""
    session = get_session()
    with session.begin():
        (session.query(models.UserToGroup).
         filter_by(user_openid=user_openid).
         filter_by(group_id=group_id).
         delete(synchronize_session=False))


def add_organization(organization_info, creator):
    """Add organization."""
    session = get_session()
    with session.begin():
        group = models.Group()
        group.name = 'Group for %s' % organization_info['name']
        group.save(session=session)
        group_id = group.id

        item = models.UserToGroup()
        item.user_openid = creator
        item.group_id = group_id
        item.created_by_user = creator
        item.save(session=session)

        organization = models.Organization()
        organization.type = organization_info.get(
            'type', api_const.PRIVATE_VENDOR)
        organization.name = organization_info['name']
        organization.description = organization_info.get('description')
        organization.group_id = group_id
        organization.created_by_user = creator
        organization.properties = organization_info.get('properties')
        organization.save(session=session)

        return _to_dict(organization)


def update_organization(organization_info):
    """Update organization."""
    session = get_session()
    _id = organization_info['id']
    organization = (session.query(models.Organization).
                    filter_by(id=_id).first())
    if organization is None:
        raise NotFound('Organization with id %s not found' % _id)

    with session.begin():
        organization.type = organization_info.get(
            'type', organization.type)
        organization.name = organization_info.get(
            'name', organization.name)
        organization.description = organization_info.get(
            'description', organization.description)
        organization.properties = organization_info.get(
            'properties', organization.properties)
        organization.save(session=session)
        return _to_dict(organization)


def get_organization(organization_id, allowed_keys=None):
    """Get organization by id."""
    session = get_session()
    organization = (session.query(models.Organization).
                    filter_by(id=organization_id).first())
    if organization is None:
        raise NotFound('Organization with id %s not found' % organization_id)
    return _to_dict(organization, allowed_keys=allowed_keys)


def delete_organization(organization_id):
    """delete organization by id."""
    session = get_session()
    with session.begin():
        product_ids = (session
                       .query(models.Product.id)
                       .filter_by(organization_id=organization_id))
        (session.query(models.ProductVersion).
         filter(models.ProductVersion.product_id.in_(product_ids)).
         delete(synchronize_session=False))
        (session.query(models.Product).
         filter_by(organization_id=organization_id).
         delete(synchronize_session=False))
        (session.query(models.Organization).
         filter_by(id=organization_id).
         delete(synchronize_session=False))


def add_product(product_info, creator):
    """Add product."""
    product = models.Product()
    product.id = str(uuid.uuid4())
    product.type = product_info['type']
    product.product_type = product_info['product_type']
    product.product_ref_id = product_info.get('product_ref_id')
    product.name = product_info['name']
    product.description = product_info.get('description')
    product.organization_id = product_info['organization_id']
    product.created_by_user = creator
    product.public = product_info.get('public', False)
    product.properties = product_info.get('properties')

    session = get_session()
    with session.begin():
        product.save(session=session)
        product_version = models.ProductVersion()
        product_version.created_by_user = creator
        product_version.version = product_info.get('version')
        product_version.product_id = product.id
        product_version.save(session=session)

        return _to_dict(product)


def update_product(product_info):
    """Update product by id."""
    session = get_session()
    _id = product_info.get('id')
    product = session.query(models.Product).filter_by(id=_id).first()
    if product is None:
        raise NotFound('Product with id %s not found' % _id)

    keys = ['name', 'description', 'product_ref_id', 'public', 'properties']
    for key in keys:
        if key in product_info:
            setattr(product, key, product_info[key])

    with session.begin():
        product.save(session=session)
        return _to_dict(product)


def get_product(id, allowed_keys=None):
    """Get product by id."""
    session = get_session()
    product = session.query(models.Product).filter_by(id=id).first()
    if product is None:
        raise NotFound('Product with id "%s" not found' % id)
    return _to_dict(product, allowed_keys=allowed_keys)


def delete_product(id):
    """delete product by id."""
    session = get_session()
    with session.begin():
        (session.query(models.ProductVersion)
         .filter_by(product_id=id)
         .delete(synchronize_session=False))
        (session.query(models.Product).filter_by(id=id).
         delete(synchronize_session=False))


def get_foundation_users():
    """Get users' openid-s that belong to group of foundation."""
    session = get_session()
    organization = (
        session.query(models.Organization.group_id)
        .filter_by(type=api_const.FOUNDATION).first())
    if organization is None:
        LOG.warning('Foundation organization record not found in DB.')
        return []
    group_id = organization.group_id
    users = (session.query(models.UserToGroup.user_openid).
             filter_by(group_id=group_id))
    return [user.user_openid for user in users]


def get_organization_users(organization_id):
    """Get users that belong to group of organization."""
    session = get_session()
    organization = (session.query(models.Organization.group_id)
                    .filter_by(id=organization_id).first())
    if organization is None:
        raise NotFound('Organization with id %s is not found'
                       % organization_id)
    group_id = organization.group_id
    users = (session.query(models.UserToGroup, models.User)
             .join(models.User,
                   models.User.openid == models.UserToGroup.user_openid)
             .filter(models.UserToGroup.group_id == group_id))
    keys = ['openid', 'fullname', 'email']
    return {item[1].openid: _to_dict(item[1], allowed_keys=keys)
            for item in users}


def get_organizations(allowed_keys=None):
    """Get all organizations."""
    session = get_session()
    items = (
        session.query(models.Organization)
        .order_by(models.Organization.created_at.desc()).all())
    return _to_dict(items, allowed_keys=allowed_keys)


def get_organizations_by_types(types, allowed_keys=None):
    """Get organization by list of types."""
    session = get_session()
    items = (
        session.query(models.Organization)
        .filter(models.Organization.type.in_(types))
        .order_by(models.Organization.created_at.desc()).all())
    return _to_dict(items, allowed_keys=allowed_keys)


def get_organizations_by_user(user_openid, allowed_keys=None):
    """Get organizations for specified user."""
    session = get_session()
    items = (
        session.query(models.Organization, models.Group, models.UserToGroup)
        .join(models.Group,
              models.Group.id == models.Organization.group_id)
        .join(models.UserToGroup,
              models.Group.id == models.UserToGroup.group_id)
        .filter(models.UserToGroup.user_openid == user_openid)
        .order_by(models.Organization.created_at.desc()).all())
    items = [item[0] for item in items]
    return _to_dict(items, allowed_keys=allowed_keys)


def get_products(allowed_keys=None, filters=None):
    """Get products based on passed in filters."""
    if filters is None:
        filters = {}
    expected_filters = ['public', 'organization_id']
    filter_args = {}
    for key, value in six.iteritems(filters):
        if key not in expected_filters:
            raise Exception('Unknown filter key "%s"' % key)
        filter_args[key] = value

    session = get_session()
    query = session.query(models.Product)
    if filter_args:
        query = query.filter_by(**filter_args)
    items = query.order_by(models.Product.created_at.desc()).all()
    return _to_dict(items, allowed_keys=allowed_keys)


def get_products_by_user(user_openid, allowed_keys=None, filters=None):
    """Get products that a user can manage."""
    if filters is None:
        filters = {}
    session = get_session()
    query = (
        session.query(models.Product, models.Organization, models.Group,
                      models.UserToGroup)
        .join(models.Organization,
              models.Organization.id == models.Product.organization_id)
        .join(models.Group,
              models.Group.id == models.Organization.group_id)
        .join(models.UserToGroup,
              models.Group.id == models.UserToGroup.group_id)
        .filter(models.UserToGroup.user_openid == user_openid))

    expected_filters = ['organization_id']
    for key, value in six.iteritems(filters):
        if key not in expected_filters:
            raise Exception('Unknown filter key "%s"' % key)
        query = query.filter(getattr(models.Product, key) ==
                             filters[key])
    items = query.order_by(models.Organization.created_at.desc()).all()
    items = [item[0] for item in items]
    return _to_dict(items, allowed_keys=allowed_keys)


def get_product_by_version(product_version_id, allowed_keys=None):
    """Get product info from a product version ID."""
    session = get_session()
    product = (session.query(models.Product).join(models.ProductVersion)
               .filter(models.ProductVersion.id == product_version_id).first())
    return _to_dict(product, allowed_keys=allowed_keys)


def get_product_version(product_version_id, allowed_keys=None):
    """Get details of a specific version given the id."""
    session = get_session()
    version = (
        session.query(models.ProductVersion)
        .filter_by(id=product_version_id).first()
    )
    if version is None:
        raise NotFound('Version with id "%s" not found' % product_version_id)
    return _to_dict(version, allowed_keys=allowed_keys)


def get_product_version_by_cpid(cpid, allowed_keys=None):
    """Get a product version given a cloud provider id."""
    session = get_session()
    version = (
        session.query(models.ProductVersion)
        .filter_by(cpid=cpid).all()
    )
    return _to_dict(version, allowed_keys=allowed_keys)


def get_product_versions(product_id, allowed_keys=None):
    """Get all versions for a product."""
    session = get_session()
    version_info = (
        session.query(models.ProductVersion)
        .filter_by(product_id=product_id).all()
    )
    return _to_dict(version_info, allowed_keys=allowed_keys)


def add_product_version(product_id, version, creator, cpid, allowed_keys=None):
    """Add a new product version."""
    product_version = models.ProductVersion()
    product_version.created_by_user = creator
    product_version.version = version
    product_version.product_id = product_id
    product_version.cpid = cpid
    session = get_session()
    with session.begin():
        product_version.save(session=session)
        return _to_dict(product_version, allowed_keys=allowed_keys)


def update_product_version(product_version_info):
    """Update product version from product_info_version dictionary."""
    session = get_session()
    _id = product_version_info.get('id')
    version = session.query(models.ProductVersion).filter_by(id=_id).first()
    if version is None:
        raise NotFound('Product version with id %s not found' % _id)

    # Only allow updating cpid.
    keys = ['cpid']
    for key in keys:
        if key in product_version_info:
            setattr(version, key, product_version_info[key])

    with session.begin():
        version.save(session=session)
        return _to_dict(version)


def delete_product_version(product_version_id):
    """Delete a product version."""
    session = get_session()
    with session.begin():
        (session.query(models.ProductVersion).filter_by(id=product_version_id).
         delete(synchronize_session=False))
