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

from docker_buildfile import DockerBuildFile
import json
import os
from refstack.models import Test
from refstack.refstack_config import RefStackConfig

config_data = RefStackConfig()

# Common tempest conf values to be used for all tests
# - Image user and password can be set to any value for testing purpose
# - We do not test OpenStack CLI
# Vendors running their own Refstack can override these using config file.
common_tempest_conf = {
    "compute":
    {
        "image_ssh_user": "root",
        "image_ssh_password": "password",
        "image_alt_ssh_user": "root",
        "image_alt_ssh_password": "password"
    },
    "cli":
    {
        "enabled": "False"
    }
}


class TempestTester(object):
    '''Utility class to handle tempest test.'''

    test_id = None
    test_obj = None

    def __init__(self, test_id):
        '''Extract the corresponding test object from the db.'''
        if test_id:
            self.test_obj = Test.query.filter_by(id=test_id).first()
            if self.test_obj:
                self.test_id = test_id
                return
        raise ValueError('Invalid test id %s' % (test_id))

    def generate_miniconf(self):
        '''Return a JSON object representing the mini tempest conf.'''

        # Get custom tempest config from config file
        custom_tempest_conf = config_data.get_tempest_config()

        # Construct cloud specific tempest config from db
        if self.test_obj.cloud:
            cloud_tempest_conf = {
                "identity":
                {
                    "uri": self.test_obj.cloud.endpoint,
                    "uri_v3": self.test_obj.cloud.endpoint_v3,
                    "username": self.test_obj.cloud.test_user,
                    "alt_username": self.test_obj.cloud.test_user,
                    "admin_username": self.test_obj.cloud.admin_user
                }
            }
        else:
            cloud_tempest_conf = dict()

        # Merge all the config data together
        # - Start with common config
        # - Insert/Overwrite with values from custom config
        # - Insert/Overwrite with values from cloud DB
        tempest_conf = common_tempest_conf
        self._merge_config(tempest_conf, custom_tempest_conf)
        self._merge_config(tempest_conf, cloud_tempest_conf)

        return json.dumps(tempest_conf)

    def _merge_config(self, dic1, dic2):
        '''Insert data from dictionary dic2 into dictionary dic1.

            dic1 and dic2 are in the format of section, key, value.
        '''
        if not all([dic1, dic2]):
            return

        for section, data in dic2.items():
            if section in dic1:
                dic1[section].update(data)
            else:
                dic1.update({section: data})

    def generate_testcases(self):
        '''Return a JSON array of the tempest testcases to be executed.'''

        # Set to full tempest test unless it is specified in the config file
        testcases = config_data.get_tempest_testcases()
        if not testcases:
            testcases = {"testcases": ["tempest"]}

        return json.dumps(testcases)

    def process_resultfile(self, filename):
        '''Process the tempest result file.'''

        ''' TODO: store the file in test db obj '''
        ''' ForNow: write the file to console output '''
        with open(filename, 'r') as f:
            print f.read()
            f.close()

    def execute_test(self, extraConfJSON=None):
        '''Execute the tempest test with the provided extraConfJSON.'''

        options = {'DOCKER': self._execute_test_docker,
                   'LOCAL': self._execute_test_local,
                   'GEARMAN': self._execute_test_gearman}

        ''' TODO: Initial test status in DB '''

        if config_data.get_test_mode():
            test_mode = config_data.get_test_mode().upper()
        else:
            # Default to use docker if not specified in the config file
            test_mode = 'DOCKER'

        try:
            options[test_mode](extraConfJSON)
        except KeyError:
            print 'Error: Invalid test mode in config file'

        ''' TODO: Update test status in DB'''

    def _execute_test_docker(self, extraConfJSON=None):
        '''Execute the tempest test in a docker container.'''

        ''' Create the docker build file '''
        docker_file = os.path.join(config_data.get_working_dir(),
                                   'test_%s.docker_file' % self.test_id)
        docker_builder = DockerBuildFile()
        docker_builder.test_id = self.test_id
        docker_builder.api_server_address = config_data.get_app_address()
        ''' TODO: Determine tempest URL based on the cloud version '''
        ''' ForNow: Use the Tempest URL in the config file '''
        docker_builder.tempest_code_url = config_data.get_tempest_url()
        docker_builder.confJSON = extraConfJSON
        docker_builder.build_docker_buildfile(docker_file)

        ''' Execute the docker build file '''
        out_file = os.path.join(config_data.get_working_dir(),
                                'test_%s.dockerOutput' % self.test_id)
        docker_tag = 'refstack_%s' % (self.test_id)

        cmd = 'nohup sh -c "docker build -t %s - < %s ' \
              '&& docker run -t %s" > %s &' % (docker_tag, docker_file,
                                               docker_tag, out_file)
        os.system(cmd)
        print cmd

        ''' TODO: Clean up the temporary docker build and output file '''

    def _execute_test_local(self, extraConfJSON=None):
        '''Execute the tempest test locally.'''
        pass

    def _execute_test_gearman(self, extraConfJSON=None):
        '''Execute the tempest test with gearman.'''
        pass
