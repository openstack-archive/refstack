# Copyright (c) 2016 IBM, Inc.
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

"""Class for retrieving DefCore guideline information."""

from oslo_config import cfg
from oslo_log import log
import re
import requests
import requests_cache

CONF = cfg.CONF
LOG = log.getLogger(__name__)

# Cached requests will expire after 12 hours.
requests_cache.install_cache(cache_name='github_cache',
                             backend='memory',
                             expire_after=43200)


class Guidelines:
    """This class handles guideline/capability listing and retrieval."""

    def __init__(self,
                 repo_url=None,
                 raw_url=None):
        """Initialize class with needed URLs.

        The URL for the guidelines repository is specified with 'repo_url'.
        The URL for where raw files are served is specified with 'raw_url'.
        These values will default to the values specified in the RefStack
        config file.
        """
        if repo_url:
            self.repo_url = repo_url
        else:
            self.repo_url = CONF.api.github_api_capabilities_url

        if raw_url:
            self.raw_url = raw_url
        else:
            self.raw_url = CONF.api.github_raw_base_url

    def get_guideline_list(self):
        """Return a list of a guideline files.

        The repository url specificed in class instantiation is checked
        for a list of JSON guideline files. A list of these is returned.
        """
        try:
            response = requests.get(self.repo_url)
            LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                      (response.status_code,
                       getattr(response, 'from_cache', False)))
            if response.status_code == 200:
                regex = re.compile('^([0-9]{4}\.[0-9]{2}|next)\.json$')
                capability_files = []
                for rfile in response.json():
                    if rfile["type"] == "file" and regex.search(rfile["name"]):
                        capability_files.append(rfile["name"])
                return capability_files
            else:
                LOG.warning('Guidelines repo URL (%s) returned non-success '
                            'HTTP code: %s' % (self.repo_url,
                                               response.status_code))
                return None

        except requests.exceptions.RequestException as e:
            LOG.warning('An error occurred trying to get repository contents '
                        'through %s: %s' % (self.repo_url, e))
            return None

    def get_guideline_contents(self, guideline_file):
        """Get JSON data from raw guidelines URL."""
        file_url = ''.join((self.raw_url.rstrip('/'),
                            '/', guideline_file, ".json"))
        try:
            response = requests.get(file_url)
            LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                      (response.status_code,
                       getattr(response, 'from_cache', False)))
            if response.status_code == 200:
                return response.json()
            else:
                LOG.warning('Raw guideline URL (%s) returned non-success HTTP '
                            'code: %s' % (self.raw_url, response.status_code))
                return None
        except requests.exceptions.RequestException as e:
            LOG.warning('An error occurred trying to get raw capability file '
                        'contents from %s: %s' % (self.raw_url, e))
            return None

    def get_target_capabilities(self, guideline_json, types=None,
                                target='platform'):
        """Get list of capabilities that match the given statuses and target.

        If no list of types in given, then capabilities of all types
        are given. If not target is specified, then all capabilities are given.
        """
        components = guideline_json['components']
        targets = set()
        if target != 'platform':
            targets.add(target)
        else:
            targets.update(guideline_json['platform']['required'])

        target_caps = set()
        for component in targets:
            for status, capabilities in components[component].items():
                if types is None or status in types:
                    target_caps.update(capabilities)

        return list(target_caps)

    def get_test_list(self, guideline_json, capabilities=[],
                      alias=True, show_flagged=True):
        """Generate a test list based on input.

        A test list is formed from the given guideline JSON data and
        list of capabilities. If 'alias' is True, test aliases are
        included in the list. If 'show_flagged' is True, flagged tests are
        included in the list.
        """
        caps = guideline_json['capabilities']
        schema = guideline_json['schema']
        test_list = []
        for cap, cap_details in caps.items():
            if cap in capabilities:
                if schema == '1.2':
                    for test in cap_details['tests']:
                        if show_flagged:
                            test_list.append(test)
                        elif not show_flagged and \
                            test not in cap_details['flagged']:
                            test_list.append(test)
                else:
                    for test, test_details in cap_details['tests'].items():
                        added = False
                        if test_details.get('flagged'):
                            if show_flagged:
                                test_str = '{}[{}]'.format(
                                    test,
                                    test_details.get('idempotent_id', '')
                                )
                                test_list.append(test_str)
                                added = True
                        else:
                            # Make sure the test UUID is in the test string.
                            test_str = '{}[{}]'.format(
                                test,
                                test_details.get('idempotent_id', '')
                            )
                            test_list.append(test_str)
                            added = True

                        if alias and test_details.get('aliases') and added:
                            for alias in test_details['aliases']:
                                test_str = '{}[{}]'.format(
                                    alias,
                                    test_details.get('idempotent_id', '')
                                )
                                test_list.append(test_str)
        test_list.sort()
        return test_list
