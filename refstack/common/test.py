#
# Copyright (c) 2013 Piston Cloud Computing, Inc.
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
from refstack.common.tempest_config import TempestConfig


class Test(object):
    """ Test functions"""
    test_id = None
    sha = None
    cloud_id = None
    _status = None


    def __init__(self,cloud_id=None,test_id=None,sha=None):
        """ init method loads specified id or fails"""
        if not test_id:
            #create a new test id
            self.test_id = 10
        else: 
            # set test id
            self.test_id = id

        self.tempest_config = TempestConfig()
        self.cloud_id = cloud_id
        self.sha = sha


    def run_remote(self):
        """triggers remote run"""  
        # install tempest in virt env
        # start tests against cloud_id using sha of tempest 
        # no sha indicates trunk


    def run_local():
        """ triggers local run"""
        # generates config
        
        # write to disk (this should cleanly invoke tempest with this config instead and then )
        
        
        return "run_local called"




    def cancel(self):
        """ cancels a running test"""


    @property
    def status(self):
        """The status property."""
        def fget(self):
            return self._status
        def fset(self, value):
            self._status = value
        def fdel(self):
            del self._status
        return locals()


    @property
    def config(self):
        """The config property. outputs a tempest config based on settings"""    
        return self.tempest_config.output()

