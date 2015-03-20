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


###################
def store_results(results):
    """Storing results into database.

    :param results: Dict describes test results.
    """
    return IMPL.store_results(results)


def get_test(test_id):
    """Get test information from the database.

    :param test_id: The ID of the test.
    """
    return IMPL.get_test(test_id)


def get_test_results(test_id):
    """Get all passed tempest tests for a particular test.

    :param test_id: The ID of the test.
    """
    return IMPL.get_test_results(test_id)


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
