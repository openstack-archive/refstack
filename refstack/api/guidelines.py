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

"""Class for retrieving Interop WG guideline information."""

import itertools
from oslo_config import cfg
from oslo_log import log
from operator import itemgetter
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
                 raw_url=None,
                 additional_capability_urls=None):
        """Initialize class with needed URLs.

        The URL for the guidelines repository is specified with 'repo_url'.
        The URL for where raw files are served is specified with 'raw_url'.
        These values will default to the values specified in the RefStack
        config file.
        """
        self.guideline_sources = list()
        if additional_capability_urls:
            self.additional_urls = additional_capability_urls.split(',')
        else:
            self.additional_urls = \
                CONF.api.additional_capability_urls.split(',')
        [self.guideline_sources.append(url) for url in self.additional_urls]
        if repo_url:
            self.repo_url = repo_url
        else:
            self.repo_url = CONF.api.github_api_capabilities_url
        if self.repo_url and self.repo_url not in self.guideline_sources:
            self.guideline_sources.append(self.repo_url)
        if raw_url:
            self.raw_url = raw_url
        else:
            self.raw_url = CONF.api.github_raw_base_url

    def get_guideline_list(self):
        """Return a list of a guideline files.

        The repository url specificed in class instantiation is checked
        for a list of JSON guideline files. A list of these is returned.
        """
        capability_files = {}
        capability_list = []
        powered_files = []
        addon_files = []
        for src_url in self.guideline_sources:
            try:
                resp = requests.get(src_url)

                LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                          (resp.status_code,
                           getattr(resp, 'from_cache', False)))
                if resp.status_code == 200:
                    regex = re.compile('([0-9]{4}\.[0-9]{2}|next)\.json')
                    for rfile in resp.json():
                        if rfile["type"] == "file" and \
                                regex.search(rfile["name"]):
                            if 'add-ons' in rfile['path'] and \
                                    rfile[
                                        'name'] not in map(itemgetter('name'),
                                                           addon_files):
                                file_dict = {'name': rfile['name']}
                                addon_files.append(file_dict)
                            elif 'add-ons' not in rfile['path'] and \
                                rfile['name'] not in map(itemgetter('name'),
                                                         powered_files):
                                file_dict = {'name': rfile['name'],
                                             'file': rfile['path']}
                                powered_files.append(file_dict)
                else:
                    LOG.warning('Guidelines repo URL (%s) returned '
                                'non-success HTTP code: %s' %
                                (src_url, resp.status_code))

            except requests.exceptions.RequestException as e:
                LOG.warning('An error occurred trying to get repository '
                            'contents through %s: %s' % (src_url, e))
        for k, v in itertools.groupby(addon_files,
                                      key=lambda x: x['name'].split('.')[0]):
            values = [{'name': x['name'].split('.', 1)[1], 'file': x['name']}
                      for x in list(v)]
            capability_list.append((k, list(values)))
        capability_list.append(('powered', powered_files))
        capability_files = dict((x, y) for x, y in capability_list)
        return capability_files

    def get_guideline_contents(self, gl_file):
        """Get contents for a given guideline path."""
        if '.json' not in gl_file:
            gl_file = '.'.join((gl_file, 'json'))
        regex = re.compile("[a-z]*\.([0-9]{4}\.[0-9]{2}|next)\.json")
        if regex.search(gl_file):
            guideline_path = 'add-ons/' + gl_file
        else:
            guideline_path = gl_file

        file_url = ''.join((self.raw_url.rstrip('/'),
                            '/', guideline_path))
        LOG.debug("file_url: %s" % (file_url))
        try:
            response = requests.get(file_url)
            LOG.debug("Response Status: %s / Used Requests Cache: %s" %
                      (response.status_code,
                       getattr(response, 'from_cache', False)))
            LOG.debug("Response body: %s" % str(response.text))
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
        if ('metadata' in guideline_json and
                guideline_json['metadata']['schema'] >= '2.0'):
            schema = guideline_json['metadata']['schema']
            platformsMap = {
                'platform': 'OpenStack Powered Platform',
                'compute': 'OpenStack Powered Compute',
                'object': 'OpenStack Powered Storage',
                'dns': 'OpenStack with DNS',
                'orchestration': 'OpenStack with Orchestration'

            }
            if target == 'dns' or target == 'orchestration':
                targets = ['os_powered_' + target]
            else:
                comps = \
                    guideline_json['platforms'][platformsMap[target]
                                                ]['components']
                targets = (obj['name'] for obj in comps)
        else:
            schema = guideline_json['schema']
            targets = set()
            if target != 'platform':
                targets.add(target)
            else:
                targets.update(guideline_json['platform']['required'])
        target_caps = set()
        for component in targets:
            complist = components[component]
            if schema >= '2.0':
                complist = complist['capabilities']
            for status, capabilities in complist.items():
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
        if ('metadata' in guideline_json and
                guideline_json['metadata']['schema'] >= '2.0'):
            schema = guideline_json['metadata']['schema']
        else:
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
