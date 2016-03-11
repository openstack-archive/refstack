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

"""Defcore guidelines controller."""

from oslo_log import log
import pecan
from pecan import rest

from refstack.api import guidelines

LOG = log.getLogger(__name__)


class GuidelinesController(rest.RestController):
    """/v1/guidelines handler.

    This acts as a proxy for retrieving guideline files
    from the openstack/defcore Github repository.
    """

    @pecan.expose('json')
    def get(self):
        """Get a list of all available guidelines."""
        g = guidelines.Guidelines()
        version_list = g.get_guideline_list()
        if version_list is None:
            pecan.abort(500, 'The server was unable to get a list of '
                             'guidelines from the external source.')
        else:
            return version_list

    @pecan.expose('json')
    def get_one(self, file_name):
        """Handler for getting contents of specific guideline file."""
        g = guidelines.Guidelines()
        json = g.get_guideline_contents(file_name)
        if json:
            return json
        else:
            pecan.abort(500, 'The server was unable to get the JSON '
                             'content for the specified guideline file.')
