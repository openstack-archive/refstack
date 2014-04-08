#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014 IBM Corp.
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

import argparse
import ConfigParser
import fnmatch
import json
import logging
import os
import requests
import subprocess
import sys
import time
import urllib2


class Test:
    def __init__(self, args):
        '''Prepare a tempest test against a cloud.'''

        log_format = "%(asctime)s %(name)s %(levelname)s %(message)s"
        self.logger = logging.getLogger("execute_test")
        console_log_handle = logging.StreamHandler()
        console_log_handle.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(console_log_handle)
        if os.environ.get("DEBUG"):
            self.logger.setLevel(logging.DEBUG)
        elif args.verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.CRITICAL)

        self.app_server_address = None
        self.test_id = None
        if args.callback:
            self.app_server_address, self.test_id = args.callback

        self.mini_conf_dict = json.loads(self.get_mini_config())
        self.extra_conf_dict = dict()
        if args.conf_json:
            self.extra_conf_dict = args.conf_json

        self.testcases = {"testcases": ["tempest"]}
        if args.testcases:
            self.testcases = {"testcases": args.testcases}

        self.tempest_home =\
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempest')

        if args.tempest_home:
            self.tempest_home = args.tempest_home

        self.sample_conf_file = os.path.join(self.tempest_home, 'etc',
                                             'tempest.conf.sample')
        self.tempest_conf_file = os.path.join(self.tempest_home,
                                              'tempest.config')
        self.result_dir = os.path.join(self.tempest_home, '.testrepository')
        self.result = os.path.join(self.result_dir, 'result')
        self.tempest_script = os.path.join(self.tempest_home, 'run_tests.sh')
        self.sample_conf_parser = ConfigParser.SafeConfigParser()
        self.sample_conf_parser.read(self.sample_conf_file)

    def gen_config(self):
        '''Merge mini config, extra config, tempest.conf.sample
           and write to tempest.config.
        '''
        self.logger.info('Generating tempest.config')
        self.merge_to_sample_conf(self.mini_conf_dict)
        self.merge_to_sample_conf(self.extra_conf_dict)
        # discovered config will not overwrite the value in the
        # mini_conf_dict and extra_conf_dict
        discovered_conf_dict = self._build_discovered_dict_conf()
        self.merge_to_sample_conf(discovered_conf_dict)
        self.sample_conf_parser.write(open(self.tempest_conf_file, 'w'))

    def merge_to_sample_conf(self, dic):
        '''Merge values in a dictionary to tempest.conf.sample.'''
        for section, data in dic.items():
            for key, value in data.items():
                if self.sample_conf_parser.has_option(section, key):
                    self.sample_conf_parser.set(section, key, value)

    def get_mini_config(self):
        '''Return a mini config in JSON string.'''
        # create config from environment variables if set
        url = os.environ.get("OS_AUTH_URL")
        if url:
            user = os.environ.get("OS_USERNAME")
            self.logger.info('Using Config ENV variables for %s@%s'
                             % (url, user))
            # for now, very limited configuration.  refactor as we add vars
            env_config = {"identity":
                          {"uri": url,
                           "username": user,
                           "password": os.environ.get("OS_PASSWORD"),
                           "tenant_name": os.environ.get("OS_TENANT_NAME"),
                           "region": os.environ.get("OS_REGION_NAME")},
                          "compute":
                          {"image_ref": os.environ.get("TEMPEST_IMAGE_REF",
                                                       "cirros")}}
            json_config = json.dumps(env_config, separators=(',', ':'))
            self.logger.debug("ENV config: %s" % (json_config))
            return json_config
        # otherwise get them from the app server
        else:
            if self.app_server_address and self.test_id:
                url = "http://%s/get-miniconf?test_id=%s" % \
                    (self.app_server_address, self.test_id)
                try:
                    req = urllib2.urlopen(url=url, timeout=10)
                    self.logger.info('Using App Server Config from %s' % (url))
                    return req.readlines()[0]
                except:
                    self.logger.critical('Failed to get mini config from %s'
                                         % url)
                    raise
            else:
                return json.dumps(dict())

    def get_test_cases(self):
        '''Return list of tempest testcases in JSON string.

           For certification, the list will contain only one test case.
           For vendor testing, the list may contain any number of test cases.
        '''
        if self.app_server_address and self.test_id:
            self.logger.info("Get test cases")
            url = "http://%s/get-testcases?test_id=%s" % \
                (self.app_server_address, self.test_id)
            try:
                req = urllib2.urlopen(url=url, timeout=10)
                return req.readlines()[0]
            except:
                self.logger.crtical('Failed to get test cases from %s' % url)
                raise
        else:
            return json.dumps(self.testcases)

    def run_test_cases(self):
        '''Executes each test case in the testcase list.'''

        # Make a backup in case previous data exists in the the directory
        if os.path.exists(self.result_dir):
            date = time.strftime("%m%d%H%M%S")
            backup_path = os.path.join(os.path.dirname(self.result_dir),
                                       "%s_backup_%s" %
                                       (os.path.basename(self.result_dir),
                                        date))
            self.logger.info("Rename existing %s to %s" %
                             (self.result_dir, backup_path))
            os.rename(self.result_dir, backup_path)

        # Execute each testcase.
        testcases = json.loads(self.get_test_cases())['testcases']
        self.logger.info('Running test cases')
        for case in testcases:
            cmd = ('%s -C %s -N -- %s' %
                   (self.tempest_script, self.tempest_conf_file, case))
            # When a testcase fails
            # continue execute all remaining cases so any partial result can be
            # reserved and posted later.
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                self.logger.error('%s %s testcases failed to complete' %
                                  (e, case))

    def post_test_result(self):
        '''Post the combined results back to the server.'''
        if self.app_server_address and self.test_id:
            self.logger.info('Send back the result')
            url = "http://%s/post-result?test_id=%s" % \
                (self.app_server_address, self.test_id)
            files = {'file': open(self.result, 'rb')}
            try:
                requests.post(url, files=files)
                self.logger.info('Result posted successfully')
            except:
                self.logger.critical('failed to post result to %s' % url)
                raise
        else:
            self.logger.info('Testr result can be found at %s' % (self.result))

    def combine_test_result(self):
        '''Generate a combined testr result.'''
        testr_results = [item for item in os.listdir(self.result_dir)
                         if fnmatch.fnmatch(item, '[0-9]*')]
        testr_results.sort(key=int)
        with open(self.result, 'w') as outfile:
            for fp in testr_results:
                with open(os.path.join(self.result_dir, fp), 'r') as infile:
                    outfile.write(infile.read())
        self.logger.info('Combined testr result')

    def run(self):
        '''Execute tempest test against the cloud.'''

        self.gen_config()

        self.run_test_cases()

        self.combine_test_result()

        self.post_test_result()

    # These methods are for identity discovery
    def _subtract_dictionaries(self, discovered_conf_dict, conf_dict):
        '''Remove the configs in conf_dict from discovered_conf_dict.'''
        for section, data in discovered_conf_dict.items():
            for key in data.keys():
                if section in conf_dict and key in conf_dict[section]:
                    self.logger.info("Will not discover [%s] %s because caller"
                                     " chose to overwrite" % (section, key))
                    del discovered_conf_dict[section][key]

    def _build_discovered_dict_conf(self):
        '''Return discovered tempest configs in a json string.'''
        self.logger.info("Starting tempest config discovery")

        # This is the default discovery items
        # in which the tempest.sample.conf will be discovered.
        discovery_conf_dict =\
            {"identity": {"region": self.get_identity_region,
                          "admin_tenant_name": self.get_admin_tenant_name,
                          "tenant_name": self.get_tenant_name,
                          "alt_tenant_name": self.get_alt_tenant_name}
             }

        # Remove the configs from the default discovery
        # for those that caller choose to overwrite.
        self._subtract_dictionaries(discovery_conf_dict, self.mini_conf_dict)
        self._subtract_dictionaries(discovery_conf_dict, self.extra_conf_dict)

        # populate configs
        for section, data in discovery_conf_dict.items():
                for key in data.keys():
                    discovery_conf_dict[section][key] =\
                        discovery_conf_dict[section][key]()
        self.logger.info("Discovered configs: %s" % discovery_conf_dict)
        return discovery_conf_dict

    def get_keystone_token(self, url, user, password, tenant=""):
        ''' Returns the json response from keystone tokens API call.'''
        parameter = {"auth": {"tenantName": tenant,
                              "passwordCredentials":
                              {"username": user,
                               "password": password}
                              }
                     }
        header = {"Content-type": "application/json"}
        try:
            req = requests.post(url, data=json.dumps(parameter),
                                headers=header)
            if req.status_code is not requests.codes.ok:
                req.raise_for_status()
        except:
            self.logger.critical("Failed to get a Keystone token. "
                                 "Please verify your keystone endpoint url,"
                                 "username or password.\n"
                                 "url: \"%s\"\nheader: %s\nparameter: %s\n"
                                 "response %s" %
                                 (url, header, parameter, req.content))
            raise

        return req.content

    def get_tenants(self, token_id):
        '''Return a list of tenants of a token_id.'''
        keystone_url = self.sample_conf_parser.get("identity", "uri")
        headers = {"Content-type": "application/json",
                   "X-Auth-Token": token_id}
        try:
            req = requests.get(keystone_url + "/tenants", headers=headers)
        except:
            self.logger.critical("failed to get tenant for token id %s"
                                 "from %s" % (token_id, keystone_url))
            raise
        return json.loads(req.content)["tenants"]

    def get_alt_tenant_name(self):
        '''Return the alt_tenant_name
        '''
        keystone_url = self.sample_conf_parser.get("identity", "uri")
        alt_user = self.sample_conf_parser.get("identity", "alt_username")
        alt_pw = self.sample_conf_parser.get("identity", "alt_password")
        token_id = json.loads(self.get_keystone_token(url=keystone_url +
                                                      "/tokens",
                                                      user=alt_user,
                                                      password=alt_pw)
                              )["access"]["token"]["id"]
        '''TODO: Assuming the user only belongs to one tenant'''
        try:
            alt_tenant = self.get_tenants(token_id)[0]["name"]
        except:
            self.logger.critical("failed to get the tenant for alt_username %s"
                                 "from %s" % (alt_user, keystone_url))
            raise
        return alt_tenant

    def get_tenant_name(self):
        '''Return the tenant_name.
        '''
        keystone_url = self.sample_conf_parser.get("identity", "uri")
        user = self.sample_conf_parser.get("identity", "username")
        pw = self.sample_conf_parser.get("identity", "password")
        token_id = json.loads(self.get_keystone_token(url=keystone_url +
                                                      "/tokens",
                                                      user=user,
                                                      password=pw)
                              )["access"]["token"]["id"]
        '''TODO: Assuming the user only belongs to one tenant'''
        try:
            tenant = self.get_tenants(token_id)[0]["name"]
        except:
            self.logger.critical("failed to get the tenant for username %s"
                                 "from %s" % (user, keystone_url))
            raise
        return tenant

    def get_admin_tenant_name(self):
        '''
        Return the admin_tenant_name.
        TODO: save admin tenant as an attribute so get_identity_region()
        method can directly use it.
        '''
        keystone_url = self.sample_conf_parser.get("identity", "uri")
        admin_user = self.sample_conf_parser.get("identity", "admin_username")
        admin_pw = self.sample_conf_parser.get("identity", "admin_password")
        token_id = json.loads(self.get_keystone_token(url=keystone_url +
                                                      "/tokens",
                                                      user=admin_user,
                                                      password=admin_pw)
                              )["access"]["token"]["id"]

        '''TODO: Authenticate as "admin" (public URL) against each tenant found
        in tanantList until a tenant is found on which "admin" has
        "admin"role. For now, assuming admin user ONLY belongs to admin tenant
        and the admin has admin role as defined in
        tempest.sample.conf.identiy.admin_role
        '''
        try:
            tenant = self.get_tenants(token_id)[0]["name"]
        except:
            self.logger.critical("failed to get the tenant for"
                                 "admin_username %s from %s" %
                                 (admin_user, keystone_url))
            raise
        return tenant

    def get_identity_region(self):
        '''Return the identity region.
        '''
        keystone_url = self.sample_conf_parser.get("identity", "uri")
        admin_user = self.sample_conf_parser.get("identity", "admin_username")
        admin_pw = self.sample_conf_parser.get("identity", "admin_password")
        admin_tenant = self.get_admin_tenant_name()
        '''
        TODO: Preserve the admin token id as an attribute because
        the admin_token will be used to for image discovery
        '''
        admin_token = json.loads(self.get_keystone_token
                                 (url=keystone_url + "/tokens",
                                  user=admin_user,
                                  password=admin_pw,
                                  tenant=admin_tenant))
        '''TODO: assume there is only one identity endpoint'''
        identity_region =\
            [service["endpoints"][0]["region"]
             for service in admin_token["access"]["serviceCatalog"]
             if service["type"] == "identity"][0]

        return identity_region

    ''' TODO: The remaining methods are for image discovery. '''
    def create_image(self):
        '''Download and create cirros image.
           Return the image reference id
        '''
        pass

    def find_smallest_flavor(self):
        '''Find the smallest flavor by sorting by memory size.
        '''
        pass

    def delete_image(self):
        '''Delete a image.
        '''
        pass

if __name__ == '__main__':
    ''' Generate tempest.conf from a tempest.conf.sample and then run test.'''
    parser = argparse.ArgumentParser(description='Starts a tempest test',
                                     formatter_class=argparse.
                                     ArgumentDefaultsHelpFormatter)
    conflict_group = parser.add_mutually_exclusive_group()

    conflict_group.add_argument("--callback",
                                nargs=2,
                                metavar=("APP_SERVER_ADDRESS", "TEST_ID"),
                                type=str,
                                help="refstack API IP address and test ID to\
                                       retrieve configurations. i.e.:\
                                       --callback 127.0.0.1:8000 1234")

    parser.add_argument("--tempest-home",
                        help="tempest directory path")

    # with nargs, arguments are returned as a list
    conflict_group.add_argument("--testcases",
                                nargs='+',
                                help="tempest test cases. Use space to\
                                separate each testcase")
    '''
    TODO: May need to decrypt/encrypt password in args.JSON_CONF
    '''
    parser.add_argument("--conf-json",
                        type=json.loads,
                        help="tempest configurations in JSON string")

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="show verbose output")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        test = Test(args)
        test.run()
