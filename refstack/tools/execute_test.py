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
import os
import requests
import subprocess
import urllib2


class Test:
    def __init__(self, args):
        '''Prepare a tempest test against a cloud.'''

        self.api_ip = args.API_IP
        self.test_id = args.TEST_ID
        self.extraConfDict = json.loads(args.JSON_CONF)
        self.miniConfDict = None

        self.tempestHome = os.path.join(os.sep, 'tempest')
        self.sampleConfFile = os.path.join(self.tempestHome, 'etc',
                                           'tempest.conf.sample')
        self.tempestConfFile = os.path.join(self.tempestHome, 'tempest.config')
        self.resultDir = os.path.join(self.tempestHome, '.testrepository')
        self.result = os.path.join(self.resultDir, 'result')
        self.tempestScript = os.path.join(self.tempestHome, 'run_tests.sh')
        self.sampleConfParser = ConfigParser.SafeConfigParser()
        self.sampleConfParser.read(self.sampleConfFile)

    def genConfig(self):
        '''Merge mini config, extra config, tempest.conf.sample
           and write to tempest.config.
        '''
        self.miniConfDict = json.loads(self.getMiniConfig())
        self.mergeToSampleConf(self.miniConfDict)
        self.mergeToSampleConf(self.extraConfDict)
        self.sampleConfParser.write(open(self.tempestConfFile, 'w'))

    def mergeToSampleConf(self, dic):
        '''Merge values in a dictionary to tempest.conf.sample.'''
        for section, data in dic.items():
            for key, value in data.items():
                if self.sampleConfParser.has_option(section, key):
                    self.sampleConfParser.set(section, key, value)

    def getMiniConfig(self):
        '''Return a mini config in JSON string.'''
        url = "http://%s/get-miniconf?test_id=%s" % (self.api_ip, self.test_id)
        j = urllib2.urlopen(url=url)
        return j.readlines()[0]

    def getTestCases(self):
        '''Return a list of tempest testcases in JSON string.

           For certification, the list will contain only one test case.
           For vendor testing, the list may contain any number of test cases.
        '''
        url = "http://%s/get-testcases?test_id=%s" % (self.api_ip,
                                                      self.test_id)
        j = urllib2.urlopen(url=url)
        return j.readlines()[0]

    def runTestCases(self):
        '''Executes each test case in the testcase list.'''
        testcases = json.loads(self.getTestCases())['testcases']
        for case in testcases:
            cmd = ('%s -C %s -N -- %s' %
                   (self.tempestScript, self.tempestConfFile, case))
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                print 'ERROR: %s' % (str(e))

    def postTestResult(self):
        '''Post the combined results back to the server.'''

        url = "http://%s/post-result?test_id=%s" % (self.api_ip, self.test_id)

        r_list = [l for l in os.listdir(self.resultDir)
                  if fnmatch.fnmatch(l, '[0-9]*')]
        r_list.sort(key=int)
        with open(self.result, 'w') as outfile:
            for r in r_list:
                with open(os.path.join(self.resultDir, r), 'r') as infile:
                    outfile.write(infile.read())
        files = {'file': open(self.result, 'rb')}
        r = requests.post(url, files=files)

    def run(self):
        '''Execute tempest test against the cloud.'''
        print 'Generating tempest.config'
        self.genConfig()
        print 'Get tempest test cases and Run test cases'
        self.runTestCases()
        print 'Send back the result'
        self.postTestResult()

    ''' TODO: The remaining methods are for image discovery. '''

    def createImage(self):
        '''Download and create cirros image.
           Return the image reference id
        '''
        pass

    def findSmallestFlavor(self):
        '''Find the smallest flavor by sorting by memory size.
        '''
        pass

    def deleteImage(self):
        '''Delete a image.
        '''
        pass

if __name__ == '__main__':
    ''' Generate tempest.conf from a tempest.conf.sample and then run test
        Example:
        execute_test.py 172.42.17.1:8000 1 '{"section":{"key":"value",..}}'
    '''
    parser = argparse.ArgumentParser(description='Starts a tempest test \
                                    associated with a test_id')
    parser.add_argument("API_IP",
                        help="refstack API server IP to retrieve \
                        configurations. i.e.: 127.0.0.1:8000")
    parser.add_argument("TEST_ID",
                        help="test ID associated with a test")
    '''
    TODO: Need to decrypt/encrypt password in the json string (args.JSON_CONF)
    '''
    parser.add_argument("JSON_CONF",
                        help="Tempest Configurations in JSON string")
    args = parser.parse_args()
    test = Test(args)
    test.run()
