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
import inspect
import os

import alembic
import alembic.config
from oslo_config import cfg
import sqlalchemy as sa
import sqlalchemy.exc
from unittest import TestCase
from webtest import TestApp

import refstack
from refstack.api import app

CONF = cfg.CONF


class FunctionalTest(TestCase):

    """Functional test case.

    Used for functional tests where you need to test your.
    literal application and its integration with the framework.
    """

    def setUp(self):
        """Test setup."""
        class TestConfig(object):
            app = {
                'root': 'refstack.api.controllers.root.RootController',
                'modules': ['refstack.api'],
                'static_root': '%(confdir)s/public',
                'template_path': '%(confdir)s/${package}/templates',
            }

        test_config = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'refstack.test.conf'
        )
        os.environ['REFSTACK_OSLO_CONFIG'] = test_config
        self.project_path = os.path.abspath(
            os.path.join(inspect.getabsfile(refstack), '..', '..'))
        self.app = TestApp(app.setup_app(TestConfig()))
        self.prepare_test_db()
        self.migrate_test_db()

    def tearDown(self):
        """Test teardown."""
        self.app.reset()

    def prepare_test_db(self):
        """Create/clear test database."""
        db_url = CONF.database.connection
        db_name = db_url.split('/')[-1]
        short_db_url = '/'.join(db_url.split('/')[0:-1])
        try:
            engine = sa.create_engine(db_url)
            conn = engine.connect()
            conn.execute('commit')
            conn.execute('drop database %s' % db_name)
            conn.close()
        except sqlalchemy.exc.OperationalError:
            pass
        finally:
            engine = sa.create_engine('/'.join((short_db_url, 'mysql')))
            conn = engine.connect()
            conn.execute('commit')
            conn.execute('create database %s' % db_name)
            conn.close()

    def migrate_test_db(self):
        """Apply migrations to test database."""
        alembic_cfg = alembic.config.Config()
        alembic_cfg.set_main_option(
            "script_location",
            os.path.join(self.project_path, 'refstack', 'db',
                         'migrations', 'alembic')
        )
        alembic_cfg.set_main_option("sqlalchemy.url",
                                    CONF.database.connection)
        alembic.command.upgrade(alembic_cfg, 'head')

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

        if not expect_errors:
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

        if not expect_errors:
            response = response.json
        return response
