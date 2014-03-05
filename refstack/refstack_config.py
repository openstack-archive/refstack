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

import json
import os.path
from refstack.utils import INSTANCE_FOLDER_PATH


class RefStackConfig(object):
    '''Utility class to process config file.'''

    refstack_config = {}

    config_file_name = os.path.join(INSTANCE_FOLDER_PATH, 'config.json')

    working_dir = os.path.join(INSTANCE_FOLDER_PATH, 'tmpfiles')

    def __init__(self, file_name=None):
        '''Load the JSON data from the config file.'''
        if file_name:
            self.config_file_name = file_name
        if os.path.isfile(self.config_file_name):
            self.refstack_config = json.load(open(self.config_file_name))
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir)

    def get_working_dir(self):
        '''Return working directory.'''
        return self.working_dir

    def get_app_address(self):
        '''Return address of the Web App server.'''
        return self.refstack_config["app_address"]

    def get_tempest_url(self):
        '''Return the URL for tempest test code download.'''
        return self.refstack_config["tempest_url"]

    def get_tempest_config(self):
        '''Return customized tempest config parameters.'''
        return self.refstack_config["tempest_config"]

    def get_tempest_testcases(self):
        '''Return a JSON of tempest testcase.'''
        return self.refstack_config["tempest_testcases"]

    def get_test_mode(self):
        '''Return the tempest test mode.'''
        return self.refstack_config["test_mode"]
