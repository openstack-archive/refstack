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


import re
import subunit
import testtools
import unittest


class TempestSubunitTestResultBase(testtools.TestResult):
    """Class to process subunit stream.

       This class is derived from testtools.TestResult.
       This class overrides all the inherited addXXX methods
       to call the new _process_result() method to process the data.

       This class is designed to be a base class.
       The _process_result() method should be overriden by the
       derived class to customize the processing.
    """

    result_type = ["SUCCESS", "FAILURE", "ERROR", "SKIP"]

    def __init__(self, stream, descriptions, verbosity):
        """Initialize with super class signature."""
        super(TempestSubunitTestResultBase, self).__init__()

    def _process_result(self, result_type, testcase, *arg):
        """Process the data.

        The value of parameter "result_type" can be SUCCESS, FAILURE,
        ERROR, or SKIP.
        It can be used to determine from which add method this is called.
        """
        pass

    def addSuccess(self, testcase):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResultBase, self).addSuccess(testcase)
        self._process_result(self.result_type[0], testcase)

    def addFailure(self, testcase, err):
        """Overwrite super class method for additional data processing."""
        if testcase.id() == 'process-returncode':
            return
        super(TempestSubunitTestResultBase, self).addFailure(testcase, err)
        self._process_result(self.result_type[1], testcase, err)

    def addError(self, testcase, err):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResultBase, self).addFailure(testcase, err)
        self._process_result(self.result_type[2], testcase, err)

    def addSkip(self, testcase, reason=None, details=None):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResultBase,
              self).addSkip(testcase, reason, details)
        self._process_result(self.result_type[3], testcase, reason, details)

    def startTest(self, testcase):
        """Overwrite super class method for additional data processing."""
        self.start_time = self._now()
        super(TempestSubunitTestResultBase, self).startTest(testcase)


class TempestSubunitTestResult(TempestSubunitTestResultBase):
    """Process subunit stream and save data into two dictionary objects.

    1) The result dictionary object:
       results={testcase_id: [status, elapsed],
                testcase_id: [status, elapsed],
                ...}
       testcase_id: the id fetched from subunit data.
                  For Tempest test: testcase_id = test_class_name + test_name
       status: status of the testcase (PASS, FAIL, FAIL_SETUP, ERROR, SKIP)
       elapsed: testcase elapsed time

    2) The summary dictionary object:
       summary={"PASS": count, "FAIL": count, "FAIL_SETUP: count",
                "ERROR": count, "SKIP": count, "Total": count}
       count: the number of occurrence
    """

    def __init__(self, stream, descriptions, verbosity):
        """Initialize with supper class signature."""
        super(TempestSubunitTestResult, self).__init__(stream, descriptions,
                                                       verbosity)
        self.start_time = None
        self.status = ["PASS", "FAIL", "FAIL_SETUP", "ERROR", "SKIP"]

        self.results = {}
        self.summary = {self.status[0]: 0, self.status[1]: 0,
                        self.status[2]: 0, self.status[3]: 0,
                        self.status[4]: 0, "Total": 0}

    def _process_result(self, result_type, testcase, *arg):
        """Process and append data to dictionary objects."""

        testcase_id = testcase.id()
        elapsed = (self._now() - self.start_time).total_seconds()
        status = result_type

        # Convert "SUCCESS" to "PASS"
        # Separate "FAILURE" into "FAIL" and "FAIL_SETUP"
        if status == self.result_type[0]:
            status = self.status[0]
        elif status == self.result_type[1]:
            if "setUpClass" in testcase_id:
                status = self.status[2]
                testcase_id = '%s.setUpClass' % \
                    (re.search('\((.*)\)', testcase_id).group(1))
            else:
                status = self.status[1]

        self.results.setdefault(testcase_id, [])
        self.results[testcase_id] = [status, elapsed]
        self.summary[status] += 1
        self.summary["Total"] += 1


class TempestSubunitTestResultTuples(TempestSubunitTestResult):
    """Process subunit stream and save data into two dictionary objects.

    1) The result dictionary object:
       results={test_classname: [(test_name, status, elapsed),
                                 (test_name, status, elapsed),...],
                test_classname: [(test_name, status, elapsed),
                                 (test_name, status, elapsed),...],
                ...}

       status: status of the testcase (PASS, FAIL, FAIL_SETUP, ERROR, SKIP)
       elapsed: testcase elapsed time

    2) The summary dictionary object:
       summary={"PASS": count, "FAIL": count, "FAIL_SETUP: count",
                "ERROR": count, "SKIP": count, "Total": count}
       count: the number of occurrence
    """

    def _process_result(self, result_type, testcase, *arg):
        """Process and append data to dictionary objects."""

        testcase_id = testcase.id()
        elapsed = round((self._now() - self.start_time).total_seconds(), 2)
        status = result_type

        # Convert "SUCCESS" to "PASS"
        # Separate "FAILURE" into "FAIL" and "FAIL_SETUP"
        if status == self.result_type[0]:
            status = self.status[0]
        elif status == self.result_type[1]:
            if "setUpClass" in testcase_id:
                status = self.status[2]
                testcase_id = '%s.setUpClass' % \
                    (re.search('\((.*)\)', testcase_id).group(1))
            else:
                status = self.status[1]

        classname, testname = testcase_id.rsplit('.', 1)

        self.results.setdefault(classname, [])
        self.results[classname].append((testname, status, elapsed))
        self.summary[status] += 1
        self.summary["Total"] += 1


class ProcessSubunitData():
    """A class to replay subunit data from a stream."""
    result = None

    def __init__(self, in_stream, test_result_class_name=
                 TempestSubunitTestResult):
        """Read and process subunit data from a stream.

        Save processed data into a class named TempestSubunitTestResult
        which is a class derived from unittest.TestResults.
        """
        test = subunit.ProtocolTestCase(in_stream, passthrough=None)
        runner = unittest.TextTestRunner(verbosity=2, resultclass=
                                         test_result_class_name)
        #Run (replay) the test from subunit stream.
        #runner,run will return an object of type "test_result_class_name"
        self.result = runner.run(test)

    def get_result(self):
        """Return an object of type test_result_class_name."""
        return self.result
