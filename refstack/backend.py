#
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

"""Backend provider."""

import logging
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from refstack import models

logger = logging.getLogger(__name__)


class Backend(object):

    """Global backend provider."""

    def __init__(self, app_config):
        """Backend factory."""
        engine = sa.create_engine(app_config['db_url'])
        self.session_maker = orm.sessionmaker()
        self.session_maker.configure(bind=engine)

    def create_local(self):
        """Create request-local Backend instance."""
        return LocalBackend(self)


class LocalBackend(object):

    """Request-local backend provider."""

    def __init__(self, global_backend):
        """Request-local backend instance."""
        self.db_session = global_backend.session_maker()

    def store_results(self, results):
        """Storing results into database.

        :param results: Dict describes test results.
        """
        session = self.db_session

        test_id = str(uuid.uuid4())
        test = models.Test(id=test_id, cpid=results.get('cpid'),
                           duration_seconds=results.get('duration_seconds'))
        test_results = results.get('results', [])
        for result in test_results:
            session.add(models.TestResults(
                test_id=test_id, name=result['name'],
                uid=result.get('uid', None)
            ))
        session.add(test)
        session.commit()
        return test_id

    def get_test(self, test_id):
        """Get test information from the database.

        :param test_id: The ID of the test.
        """
        test_info = self.db_session.query(models.Test).\
            filter_by(id=test_id).first()
        return test_info

    def get_test_results(self, test_id):
        """Get all passed tempest tests for a particular test.

        :param test_id: The ID of the test.
        """
        results = self.db_session.query(models.TestResults.name).filter_by(
            test_id=test_id).all()
        return results
