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

"""Base classes for API tests."""
import os

from oslo_config import fixture as config_fixture
from oslotest import base
import pecan.testing
from sqlalchemy.engine import reflection
from sqlalchemy import create_engine
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint,
)

from refstack.db import migration


class FunctionalTest(base.BaseTestCase):
    """Base class for functional test case.

    Used for functional tests where you need to test your.
    literal application and its integration with the framework.
    """

    def setUp(self):
        """Test setup."""
        super(FunctionalTest, self).setUp()

        self.connection = os.environ.get("REFSTACK_TEST_MYSQL_URL")
        if self.connection is None:
            raise ValueError("Database connection url was not found. "
                             "Environment variable REFSTACK_TEST_MYSQL_URL "
                             "is not defined")

        self.config = {
            'app': {
                'root': 'refstack.api.controllers.root.RootController',
                'modules': ['refstack.api'],
            }
        }
        self.config_fixture = config_fixture.Config()
        self.CONF = self.useFixture(self.config_fixture).conf
        self.CONF.set_override('connection',
                               self.connection,
                               'database')

        self.app = pecan.testing.load_test_app(self.config)

        self.drop_all_tables_and_constraints()
        migration.upgrade('head')

    def tearDown(self):
        """Test teardown."""
        super(FunctionalTest, self).tearDown()
        pecan.set_config({}, overwrite=True)
        self.app.reset()

    def drop_all_tables_and_constraints(self):
        """Drop tables and cyclical constraints between tables."""
        engine = create_engine(self.connection)
        conn = engine.connect()
        trans = conn.begin()

        inspector = reflection.Inspector.from_engine(engine)
        metadata = MetaData()

        tbs = []
        all_fks = []

        try:
            for table_name in inspector.get_table_names():
                fks = []
                for fk in inspector.get_foreign_keys(table_name):
                    if not fk['name']:
                        continue
                    fks.append(
                        ForeignKeyConstraint((), (), name=fk['name']))

                t = Table(table_name, metadata, *fks)
                tbs.append(t)
                all_fks.extend(fks)

            for fkc in all_fks:
                conn.execute(DropConstraint(fkc))

            for table in tbs:
                conn.execute(DropTable(table))

            trans.commit()
            trans.close()
            conn.close()
        except:
            trans.rollback()
            conn.close()
            raise

    def delete(self, url, headers=None, extra_environ=None,
               status=None, expect_errors=False, **params):
        """Send HTTP DELETE request.

        :param url: url path to target service
        :param headers: a dictionary of extra headers to send
        :param extra_environ: a dictionary of environmental variables that
                              should be added to the request
        :param status: integer or string of the HTTP status code you expect
                       in response (if not 200 or 3xx). You can also use a
                       wildcard, like '3*' or '*'
        :param expect_errors: boolean value, if this is False, then if
                              anything is written to environ wsgi.errors it
                              will be an error. If it is True, then
                              non-200/3xx responses are also okay
        :param params: a query string, or a dictionary that will be encoded
                       into a query string. You may also include a URL query
                       string on the url

        """
        response = self.app.delete(url,
                                   headers=headers,
                                   extra_environ=extra_environ,
                                   status=status,
                                   expect_errors=expect_errors,
                                   params=params)

        return response

    def get_json(self, url, headers=None, extra_environ=None,
                 status=None, expect_errors=False, **params):
        """Send HTTP GET request.

        :param url: url path to target service
        :param headers: a dictionary of extra headers to send
        :param extra_environ: a dictionary of environmental variables that
                              should be added to the request
        :param status: integer or string of the HTTP status code you expect
                       in response (if not 200 or 3xx). You can also use a
                       wildcard, like '3*' or '*'
        :param expect_errors: boolean value, if this is False, then if
                              anything is written to environ wsgi.errors it
                              will be an error. If it is True, then
                              non-200/3xx responses are also okay
        :param params: a query string, or a dictionary that will be encoded
                       into a query string. You may also include a URL query
                       string on the url

        """
        response = self.app.get(url,
                                headers=headers,
                                extra_environ=extra_environ,
                                status=status,
                                expect_errors=expect_errors,
                                params=params)

        if not expect_errors and response.content_type == 'application/json':
            response = response.json
        return response

    def post_json(self, url, headers=None, extra_environ=None,
                  status=None, expect_errors=False,
                  content_type='application/json', **params):
        """Send HTTP POST request.

        :param url: url path to target service
        :param headers: a dictionary of extra headers to send
        :param extra_environ: a dictionary of environmental variables that
                              should be added to the request
        :param status: integer or string of the HTTP status code you expect
                       in response (if not 200 or 3xx). You can also use a
                       wildcard, like '3*' or '*'
        :param expect_errors: boolean value, if this is False, then if
                              anything is written to environ wsgi.errors it
                              will be an error. If it is True, then
                              non-200/3xx responses are also okay
        :param params: a query string, or a dictionary that will be encoded
                       into a query string. You may also include a URL query
                       string on the url

        """
        response = self.app.post(url,
                                 headers=headers,
                                 extra_environ=extra_environ,
                                 status=status,
                                 expect_errors=expect_errors,
                                 content_type=content_type,
                                 **params)

        if not expect_errors and response.content_type == 'application/json':
            response = response.json
        return response

    def put_json(self, url, headers=None, extra_environ=None,
                 status=None, expect_errors=False,
                 content_type='application/json', **params):
        """Send HTTP PUT request. Similar to :meth:`post_json`."""
        response = self.app.put(url,
                                headers=headers,
                                extra_environ=extra_environ,
                                status=status,
                                expect_errors=expect_errors,
                                content_type=content_type,
                                **params)

        if not expect_errors and response.content_type == 'application/json':
            response = response.json
        return response
