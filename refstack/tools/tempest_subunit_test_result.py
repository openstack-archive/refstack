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


import subunit
import testtools
import unittest


class TempestSubunitTestResult(testtools.TestResult):
    """Process subunit stream and save data into two dictionary objects.

    1) The result dictionary object:
       results={testcase_id: [status, elapsed],
                testcase_id: [status, elapsed],
                ...: ..}
       testcase_id: the id fetched from subunit data.
                  For Tempest test: testcase_id = test_class_name + test_name
       status: status of the testcase (OK, FAIL, ERROR, SKIP, FAIL_CLASS_SETUP)
       elapsed: testcase elapsed time

    2) The summary dictionary object:
       summary={"OK": count, "FAIL": count, "ERROR": count,
              "SKIP": count, "FAIL_CLASS_SETUP: count", "Total": count}
       count: the number of occurrence

    """

    def __init__(self, stream, descriptions, verbosity):
        """Initialize with supper class signature."""
        super(TempestSubunitTestResult, self).__init__()
        self.start_time = None
        self.status = ["OK", "FAIL", "ERROR", "SKIP",
                       "FAIL_CLASS_SETUP"]

        self.results = {}
        self.summary = {self.status[0]: 0, self.status[1]: 0,
                        self.status[2]: 0, self.status[3]: 0,
                        self.status[4]: 0, "Total": 0}

    def _process_result(self, status, testcase, *arg):
        """Process and append data to dictionary objects.

        User can overload this method to customize the format of the output.
        """
        testcase_id = testcase.id()
        elapsed = (self._now() - self.start_time).total_seconds()

        if (status == self.status[1]) and ("setUpClass" in testcase_id):
            status = self.status[4]
        self.results.setdefault(testcase_id, [])
        self.results[testcase_id] = [status, elapsed]

        self.summary[status] += 1
        self.summary["Total"] += 1

    def addSuccess(self, testcase):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResult, self).addSuccess(testcase)
        self._process_result(self.status[0], testcase)

    def addFailure(self, testcase, err):
        """Overwrite super class method for additional data processing."""
        if testcase.id() == 'process-returncode':
            return
        super(TempestSubunitTestResult, self).addFailure(testcase, err)
        self._process_result(self.status[1], testcase, err)

    def addError(self, testcase, err):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResult, self).addFailure(testcase, err)
        self._process_result(self.status[2], testcase, err)

    def addSkip(self, testcase, reason=None, details=None):
        """Overwrite super class method for additional data processing."""
        super(TempestSubunitTestResult,
              self).addSkip(testcase, reason, details)
        self._process_result(self.status[3], testcase, reason, details)

    def startTest(self, testcase):
        """Overwrite super class method for additional data processing."""
        self.start_time = self._now()
        super(TempestSubunitTestResult, self).startTest(testcase)


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
