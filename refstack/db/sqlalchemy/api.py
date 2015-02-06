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
"""
Implementation of SQLAlchemy backend.
"""
import sys
import uuid

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session as db_session

from refstack.db.sqlalchemy import models


CONF = cfg.CONF

_FACADE = None

_DEFAULT_SQL_CONNECTION = 'sqlite://'
db_options.set_defaults(cfg.CONF,
                        connection=_DEFAULT_SQL_CONNECTION)


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""

    return sys.modules[__name__]


###################


def store_results(results):
    test = models.Test()
    test_id = str(uuid.uuid4())
    test.id = test_id
    test.cpid = results.get('cpid')
    test.duration_seconds = results.get('duration_seconds')

    received_test_results = results.get('results', [])
    session = get_session()
    with session.begin():
        test.save(session)
        for result in received_test_results:
            test_result = models.TestResults()
            test_result.test_id = test_id
            test_result.name = result['name']
            test_result.uid = result.get('uid', None)
            test_result.save(session)
    return test_id


def get_test(test_id):
    session = get_session()
    test_info = session.query(models.Test).\
        filter_by(id=test_id).\
        first()
    return test_info


def get_test_results(test_id):
    session = get_session()
    results = session.query(models.TestResults.name).\
        filter_by(test_id=test_id).\
        all()
    return results
