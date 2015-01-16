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

"""Version 1 of the API."""
import logging

import pecan
from pecan import rest

from refstack import db

logger = logging.getLogger(__name__)


class ResultsController(rest.RestController):

    """/v1/results handler."""

    @pecan.expose('json')
    def get(self, ):
        """GET handler."""
        return {'Result': 'Ok'}

    @pecan.expose("json")
    def get_one(self, test_id):
        """Return test results in JSON format.

        :param test_id: ID of the test to get the JSON for.
        """
        test_info = db.get_test(test_id)
        if not test_info:
            pecan.abort(404)

        test_list = db.get_test_results(test_id)
        test_name_list = [test_dict[0] for test_dict in test_list]
        return {"cpid": test_info.cpid,
                "created_at": test_info.created_at,
                "duration_seconds": test_info.duration_seconds,
                "results": test_name_list}

    @pecan.expose(template='json')
    def post(self, ):
        """POST handler."""
        try:
            results = pecan.request.json
        except ValueError:
            return pecan.abort(400,
                               detail='Request body \'%s\' could not '
                                      'be decoded as JSON.'
                                      '' % pecan.request.body)
        test_id = db.store_results(results)
        return {'test_id': test_id}


class V1Controller(object):

    """Version 1 API controller root."""

    results = ResultsController()
