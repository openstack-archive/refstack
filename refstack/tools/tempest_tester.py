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
from refstack.refstack_config import RefStackConfig
import time

configData = RefStackConfig()


class TempestTester(object):
    '''Utility class to handle tempest test.'''

    test_id = None
    testObj = None
    cloudObj = None

    def __init__(self, test_id=None):
        '''Init method loads specified id.'''

        ''' If test_id exists, this is an existing test. Else this is a new
            test. Test_id wll be created later in an other module.
        '''
        if test_id:
            self.test_id = test_id
            ''' TODO: Retrieve testObj and cloudObj '''

    def generate_miniconf(self):
        '''Return a JSON object representing the mini tempest conf.'''

        ''' TODO: Construct the JSON from cloud db obj '''
        ''' ForNow: Return the JSON in vendor config '''
        conf = configData.get_tempest_config()

        return json.dumps(conf)

    def generate_testcases(self):
        '''Return a JSON array of the tempest testcases to be executed.'''

        ''' TODO: Depends on DefCore's decision, either do the full test or
                  allow users to specify what to test
        '''
        ''' ForNow: Return the JSON in vendor config '''
        conf = configData.get_tempest_testcases()

        return json.dumps(conf)

    def process_resultfile(self, filename):
        '''Process the tempest result file.'''

        ''' TODO: store the file in test db obj '''
        ''' ForNow: write the file to console output '''
        with open(filename, 'r') as f:
            print f.read()
            f.close()

    def test_cloud(self, cloud_id, extraConfJSON=None):
        '''Create and execute a new test with the provided extraConfJSON.'''

        ''' TODO: Retrieve the cloud obj from DB '''

        ''' TODO: Create new test obj in DB and get the real unique test_id'''
        ''' ForNow: use timestamp as the test_id '''
        self.test_id = time.strftime("%m%d%H%M")

        ''' invoke execute_test '''
        self.execute_test(extraConfJSON)

    def execute_test(self, extraConfJSON=None):
        '''Execute the tempest test with the provided extraConfJSON.'''

        options = {'DOCKER': self._execute_test_docker,
                   'LOCAL': self._execute_test_local,
                   'GEARMAN': self._execute_test_gearman}

        ''' TODO: Initial test status in DB '''

        try:
            options[configData.get_test_mode()](extraConfJSON)
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
