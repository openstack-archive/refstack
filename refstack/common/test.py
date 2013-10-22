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


"""Source for test results.

This abstracts the various sources of test results that Tribunal can 
read from.
"""


class UnreloadableStream(Exception):
    """The test stream can not be reloaded (probably because it is a pipe)."""


class NoStreamPresent(Exception):
    """The TestSource does not contain any subunit streams."""


class FileTestSource(object):
    """Tests results read from a file.

    Reloading re-reads the contents of the file.
    """

    def __init__(self, input_file):
        """Make a new file testsource.

        :param input_file: Open file containing test results.
        """
        fcntl.fcntl(input_file, fcntl.F_SETFL, os.O_NONBLOCK)
        self.input_file = input_file
        
    def get_subunit_stream(self):
        return self.input_file

    def reload(self):
        try:
            self.input_file.seek(0)
        except IOError, e:
            sys.stderr.write("error seeking file: %s\n" % e)
            if e.errno == errno.ESPIPE:
                raise UnreloadableStream()
            else:
                raise
        else:
            return self.input_file


class TestRepositorySource(object):
    """Get test results from a testrepository.

    Reloading asks testr to re-run (and implicitly record) a new 
    test result.

    :ivar testr_directory: path to directory containing .testr repository
    """

    def __init__(self, testr_directory):
        # Work around bug in testrepository (just filed, no # yet).
        self.testr_directory = os.path.expanduser(testr_directory)
        
    def get_subunit_stream(self):
        try:
            return self.testrepository_last_stream()
        except KeyError:
            raise NoStreamPresent()

    def reload(self):
        # run the test suite again.
        from testrepository.commands import run
        
        cmd = run.run(ui)
        # Work around 'testr run' loading to the wrong repo.
        
        here = os.getcwd()
        os.chdir(self.testr_directory)
        
        try:
            res = cmd.execute()
        finally:
            os.chdir(here)
        # Ignoring detail of exit code: the subunit parsing + ui error
        # methods will inform the user.
        if res == 3:
            # TODO: give a warning if execution failed
            # But if it went badly wrong.. something 
            return
        return self.testrepository_last_stream()

    def testrepository_last_stream(self):
        import testrepository.repository.file
        factory = testrepository.repository.file.RepositoryFactory()
        repo = factory.open(self.testr_directory)
        # this is poor because it just returns a stringio for the whole 
        # thing; we should instead try to read from it as a file so we can 
        # get nonblocking io
        return repo.get_test_run(repo.latest_id()).get_subunit_stream()



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

