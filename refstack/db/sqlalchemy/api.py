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
"""Implementation of SQLAlchemy backend."""
import sys
import uuid

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session as db_session
import six

from refstack.api import constants as api_const
from refstack.db.sqlalchemy import models


CONF = cfg.CONF

_FACADE = None

db_options.set_defaults(cfg.CONF)


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
        for k, v in six.iteritems(results.get('metadata', {})):
            meta = models.TestMeta()
            meta.meta_key, meta.value = k, v
            test.meta.append(meta)
        test.save(session)
    return test_id


def get_test(test_id):
    """Get test info."""
    session = get_session()
    test_info = session.query(models.Test).\
        filter_by(id=test_id).\
        first()
    return test_info


def get_test_results(test_id):
    """Get test results."""
    session = get_session()
    results = session.query(models.TestResults.name).\
        filter_by(test_id=test_id).\
        all()
    return results


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

    return query


def get_test_records(page, per_page, filters):
    """Get page with list of test records."""
    session = get_session()
    query = session.query(models.Test.id,
                          models.Test.created_at,
                          models.Test.cpid)

    query = _apply_filters_for_query(query, filters)
    results = query.order_by(models.Test.created_at.desc()).\
        offset(per_page * (page - 1)).\
        limit(per_page)
    return results


def get_test_records_count(filters):
    """Get total test records count."""
    session = get_session()
    query = session.query(models.Test.id)
    records_count = _apply_filters_for_query(query, filters).count()

    return records_count


class UserNotFound(Exception):

    """Raise if user not found."""

    pass


def user_get(user_openid):
    """Get user info by openid."""
    session = get_session()
    user = session.query(models.User).filter_by(openid=user_openid).first()
    if user is None:
        raise UserNotFound('User with OpenID %s not found' % user_openid)
    return user


def user_update_or_create(user_info):
    """Create user DB record if it exists, otherwise record will be updated."""
    try:
        user = user_get(user_info['openid'])
    except UserNotFound:
        user = models.User()

    session = get_session()
    with session.begin():
        user.update(user_info)
        user.save(session=session)
        return user
