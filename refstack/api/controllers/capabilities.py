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

"""Defcore capabilities controller."""

from oslo_config import cfg
from oslo_log import log
import pecan
from pecan import rest
import re
import requests
import requests_cache

CONF = cfg.CONF
LOG = log.getLogger(__name__)

# Cached requests will expire after 10 minutes.
requests_cache.install_cache(cache_name='github_cache',
                             backend='memory',
                             expire_after=600)


class CapabilitiesController(rest.RestController):
    """/v1/capabilities handler.

    This acts as a proxy for retrieving capability files
    from the openstack/defcore Github repository.
    """

    @pecan.expose('json')
    def get(self):
        """Get a list of all available capabilities."""
        try:
            response = requests.get(CONF.api.github_api_capabilities_url)
            LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                      (response.status_code,
                       getattr(response, 'from_cache', False)))
            if response.status_code == 200:
                regex = re.compile('^[0-9]{4}\.[0-9]{2}\.json$')
                capability_files = []
                for rfile in response.json():
                    if rfile["type"] == "file" and regex.search(rfile["name"]):
                        capability_files.append(rfile["name"])
                return capability_files
            else:
                LOG.warning('Github returned non-success HTTP '
                            'code: %s' % response.status_code)
                pecan.abort(response.status_code)

        except requests.exceptions.RequestException as e:
            LOG.warning('An error occurred trying to get GitHub '
                        'repository contents: %s' % e)
            pecan.abort(500)

    @pecan.expose('json')
    def get_one(self, file_name):
        """Handler for getting contents of specific capability file."""
        github_url = ''.join((CONF.api.github_raw_base_url.rstrip('/'),
                              '/', file_name, ".json"))
        try:
            response = requests.get(github_url)
            LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                      (response.status_code,
                       getattr(response, 'from_cache', False)))
            if response.status_code == 200:
                return response.json()
            else:
                LOG.warning('Github returned non-success HTTP '
                            'code: %s' % response.status_code)
                pecan.abort(response.status_code)
        except requests.exceptions.RequestException as e:
            LOG.warning('An error occurred trying to get GitHub '
                        'capability file contents: %s' % e)
            pecan.abort(500)
