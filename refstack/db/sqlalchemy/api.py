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
from oslo_db import exception as oslo_db_exc
import six

from refstack.api import constants as api_const
from refstack.db.sqlalchemy import models


CONF = cfg.CONF

_FACADE = None

db_options.set_defaults(cfg.CONF)


class NotFound(Exception):

    """Raise if item not found in db."""

    def __init__(self, model, details=None):
        """Init."""
        self.model = model
        title = details if details else ''.join((model, ' not found.'))
        super(NotFound, self).__init__(title)


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
        return [_to_dict(obj) for obj in sqlalchemy_object]
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
            elif (isinstance(value, list)
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
        raise NotFound('Test', 'Test result %s not found' % test_id)
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
            raise NotFound('Test', 'Test result %s not found' % test_id)


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
        raise NotFound('TestMeta',
                       'Metadata key %s '
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

    signed = api_const.SIGNED in filters
    if signed:
        query = (query
                 .join(models.Test.meta)
                 .filter(models.TestMeta.meta_key == api_const.PUBLIC_KEY)
                 .filter(models.TestMeta.value.in_(
                     filters[api_const.USER_PUBKEYS]))
                 )
    else:
        signed_results = (query.session
                          .query(models.TestMeta.test_id)
                          .filter_by(meta_key=api_const.PUBLIC_KEY))
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
        raise NotFound('User', 'User with OpenID %s not found' % user_openid)
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
            raise oslo_db_exc.DBDuplicateEntry(columns=['pubkeys.pubkey'],
                                               value=pubkey.pubkey)
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
