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
from refstack.extensions import db
from refstack.models import Cloud
from refstack.models import Test
from refstack.refstack_config import RefStackConfig

configData = RefStackConfig()

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
    testObj = None
    cloudObj = None

    def __init__(self, test_id=None):
        '''Init method loads specified id.

            If test_id exists, this is an existing test.
            Otherwise, this is a new test, and test_id will be created later.
        '''
        if test_id:
            self.test_id = test_id
            self.testObj = Test.query.filter_by(id=test_id).first()
            if self.testObj is not None:
                self.cloudObj = Cloud.query.filter_by(
                    id=self.testObj.cloud_id).first()

    def generate_miniconf(self):
        '''Return a JSON object representing the mini tempest conf.'''

        # Get custom tempest config from config file
        custom_tempest_conf = configData.get_tempest_config()

        # Construct cloud specific tempest config from db
        if self.cloudObj:
            cloud_tempest_conf = {
                "identity":
                {
                    "uri": self.cloudObj.endpoint,
                    "uri_v3": self.cloudObj.endpoint_v3,
                    "username": self.cloudObj.test_user,
                    "alt_username": self.cloudObj.test_user,
                    "admin_username": self.cloudObj.admin_user
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
        testcases = configData.get_tempest_testcases()
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

    def test_cloud(self, cloud_id, extraConfJSON=None):
        '''Create and execute a new test with the provided extraConfJSON.'''

        # Retrieve the cloud obj from DB
        self.cloudObj = Cloud.query.filter_by(id=cloud_id).first()

        if not self.cloudObj:
            return

        # Create new test object in DB and get the real unique test_id
        self.testObj = Test()
        self.testObj.cloud_id = self.cloudObj.id
        self.testObj.cloud = self.cloudObj
        db.session.add(self.testObj)
        db.session.commit()

        self.test_id = self.testObj.id

        # Invoke execute_test
        self.execute_test(extraConfJSON)

    def execute_test(self, extraConfJSON=None):
        '''Execute the tempest test with the provided extraConfJSON.'''

        options = {'DOCKER': self._execute_test_docker,
                   'LOCAL': self._execute_test_local,
                   'GEARMAN': self._execute_test_gearman}

        ''' TODO: Initial test status in DB '''

        if configData.get_test_mode():
            test_mode = configData.get_test_mode().upper()
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
        dockerFile = os.path.join(configData.get_working_dir(),
                                  'test_%s.dockerFile' % self.test_id)
        fileBuilder = DockerBuildFile()
        fileBuilder.test_id = self.test_id
        fileBuilder.api_server_address = configData.get_app_address()
        ''' TODO: Determine tempest URL based on the cloud version '''
        ''' ForNow: Use the Tempest URL in the config file '''
        fileBuilder.tempest_code_url = configData.get_tempest_url()
        fileBuilder.confJSON = extraConfJSON
        fileBuilder.build_docker_buildfile(dockerFile)

        ''' Execute the docker build file '''
        outFile = os.path.join(configData.get_working_dir(),
                               'test_%s.dockerOutput' % self.test_id)

        cmd = 'nohup docker build - < %s > %s &' % (dockerFile, outFile)
        os.system(cmd)
        print cmd

        ''' TODO: Clean up the temporary docker build and output file '''

    def _execute_test_local(self, extraConfJSON=None):
        '''Execute the tempest test locally.'''
        pass

    def _execute_test_gearman(self, extraConfJSON=None):
        '''Execute the tempest test with gearman.'''
        pass
