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
import os
import errno
from refstack.common.tempest_config import TempestConfig
import testrepository.repository.file
from testrepository import ui
from testrepository.commands import run
from testrepository.commands import init



class RefstackTestRepositoryUI(ui.AbstractUI):
    """A testrepository.ui.AbstractUI that glues it into Refstack.
    """

    def __init__(self, here):
        """Create a UI to run a TestRepository command under subunit_window.

        :param here: What should the 'here' be for the UI.
        """
        self.here = here

    def _check_cmd(self):
        # TODO: rewrite this .. not meant to be used the way im using it
        options = []
        self.options = optparse.Values()
        seen_options = set()
        for option, value in options:
            setattr(self.options, option, value)
            seen_options.add(option)
        if not 'quiet' in seen_options:
            setattr(self.options, 'quiet', False)
        for option in self.cmd.options:
            if not option.dest in seen_options:
                setattr(self.options, option.dest, option.default)
        
        # Arguments on self.cmd.args
        parsed_args = {}
        unparsed = []
        failed = False
        for arg in self.cmd.args:
            try:
                parsed_args[arg.name] = arg.parse(unparsed)
            except ValueError:
                failed = True
                break
        self.arguments = parsed_args
        return unparsed == [] and not failed


    def output_error(self, error_tuple):
        # Shows the error in a dialog. We could instead have a 'console' on 
        # the SubunitWindow and write the error into the console.
        import traceback
        exctype, value, tb = error_tuple
        as_string = ''.join(traceback.format_exception(exctype, value, tb))


    def output_rest(self, rest_string):
        # TODO: format as HTML, embed a browser?
        raise NotImplementedError(self.output_rest)


    def output_results(self, suite_or_test):
        # TODO: feed to the main window
        raise NotImplementedError(self.output_results)


    def output_stream(self, stream):
        # TODO: ask for a filename to save to.
        raise NotImplementedError(self.output_stream)


    def output_table(self, table):
        raise NotImplementedError(self.output_table)


    def output_values(self, values):
        # TODO: log this to the GUI somehow.
        outputs = []
        for label, value in values:
            outputs.append('%s: %s' % (label, value))
        print '%s\n' % ' '.join(outputs)


    def subprocess_Popen(self, *args, **kwargs):
        # TODO: use a GTK GIO thingy
        import subprocess
        return subprocess.Popen(*args, **kwargs)



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
        self.ui = RefstackTestRepositoryUI()

    def get_subunit_stream(self):
        try:
            return self.testrepository_last_stream()
        except KeyError:
            raise NoStreamPresent()

    def init(self):
        os.chdir(self.testr_directory)
        cmd = init.init(ui)
        cmd.execute()

    def run(self):
        here = os.getcwd()
        os.chdir(self.testr_directory)
        cmd = run.run(ui)
        try:
            res = cmd.execute()
        finally:
            os.chdir(here)


    def reload(self):
        # run the test suite again.
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
        self.tr = TestRepositorySource('/tmp/')

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

