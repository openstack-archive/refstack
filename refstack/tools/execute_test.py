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

        _format = "%(asctime)s %(name)s %(levelname)s %(message)s"
        if args.verbose:
            logging.basicConfig(level=logging.INFO, format=_format)
        else:
            logging.basicConfig(level=logging.CRITICAL, format=_format)
        self.logger = logging.getLogger("execute_test")

        self.app_server_address = None
        self.test_id = None
        if args.callback:
            self.app_server_address, self.test_id = args.callback

        self.extraConfDict = dict()
        if args.conf_json:
            self.extraConfDict = args.conf_json

        self.testcases = {"testcases": ["tempest"]}
        if args.testcases:
            self.testcases = {"testcases": args.testcases}

        self.tempestHome = os.path.join(os.path.dirname(
                                        os.path.abspath(__file__)),
                                        'tempest')
        if args.tempest_home:
            self.tempestHome = args.tempest_home

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
        self.logger.info('Generating tempest.config')
        miniConfDict = json.loads(self.getMiniConfig())
        self.mergeToSampleConf(miniConfDict)
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
        if self.app_server_address and self.test_id:
            url = "http://%s/get-miniconf?test_id=%s" % \
                (self.app_server_address, self.test_id)
            try:
                j = urllib2.urlopen(url=url, timeout=10)
                return j.readlines()[0]
            except:
                self.logger.critical('Failed to get mini config from %s' % url)
                raise
        else:
            return json.dumps(dict())

    def getTestCases(self):
        '''Return list of tempest testcases in JSON string.

           For certification, the list will contain only one test case.
           For vendor testing, the list may contain any number of test cases.
        '''
        if self.app_server_address and self.test_id:
            self.logger.info("Get test cases")
            url = "http://%s/get-testcases?test_id=%s" % \
                (self.app_server_address, self.test_id)
            try:
                j = urllib2.urlopen(url=url, timeout=10)
                return j.readlines()[0]
            except:
                self.logger.crtical('Failed to get test cases from %s' % url)
                raise
        else:
            return json.dumps(self.testcases)

    def runTestCases(self):
        '''Executes each test case in the testcase list.'''

        #Make a backup in case previous data exists in the the directory
        if os.path.exists(self.resultDir):
            date = time.strftime("%m%d%H%M%S")
            backupPath = os.path.join(os.path.dirname(self.resultDir),
                                      "%s_backup_%s" %
                                      (os.path.basename(self.resultDir), date))
            self.logger.info("Rename existing %s to %s" %
                             (self.resultDir, backupPath))
            os.rename(self.resultDir, backupPath)

        #Execute each testcase.
        testcases = json.loads(self.getTestCases())['testcases']
        self.logger.info('Running test cases')
        for case in testcases:
            cmd = ('%s -C %s -N -- %s' %
                   (self.tempestScript, self.tempestConfFile, case))
            #When a testcase fails
            #continue execute all remaining cases so any partial result can be
            #reserved and posted later.
            try:
                subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                self.logger.error('%s %s testcases failed to complete' %
                                  (e, case))

    def postTestResult(self):
        '''Post the combined results back to the server.'''
        if self.app_server_address and self.test_id:
            self.logger.info('Send back the result')
            url = "http://%s/post-result?test_id=%s" % \
                (self.app_server_address, self.test_id)
            files = {'file': open(self.result, 'rb')}
            try:
                requests.post(url, files=files)
            except:
                self.logger.critical('failed to post result to %s' % url)
                raise
        else:
            self.logger.info('Testr result can be found at %s' % (self.result))

    def combineTestrResult(self):
        '''Generate a combined testr result.'''
        r_list = [l for l in os.listdir(self.resultDir)
                  if fnmatch.fnmatch(l, '[0-9]*')]
        r_list.sort(key=int)
        with open(self.result, 'w') as outfile:
            for r in r_list:
                with open(os.path.join(self.resultDir, r), 'r') as infile:
                    outfile.write(infile.read())
        self.logger.info('Combined testr result')

    def run(self):
        '''Execute tempest test against the cloud.'''

        self.genConfig()

        self.runTestCases()

        self.combineTestrResult()

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
    '''
    parser = argparse.ArgumentParser(description='Starts a tempest test',
                                     formatter_class=argparse.
                                     ArgumentDefaultsHelpFormatter)
    conflictGroup = parser.add_mutually_exclusive_group()

    conflictGroup.add_argument("--callback",
                               nargs=2,
                               metavar=("APP_SERVER_ADDRESS", "TEST_ID"),
                               type=str,
                               help="refstack API IP address and test ID to\
                               retrieve configurations. i.e.:\
                               --callback 127.0.0.1:8000 1234")

    parser.add_argument("--tempest-home",
                        help="tempest directory path")

    #with nargs, arguments are returned as a list
    conflictGroup.add_argument("--testcases",
                               nargs='+',
                               help="tempest test cases. Use space to separate\
                               each testcase")
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
