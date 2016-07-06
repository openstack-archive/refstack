/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    angular
        .module('refstackApp')
        .controller('ResultsReportController', ResultsReportController);

    ResultsReportController.$inject = [
        '$http', '$stateParams', '$window',
        '$uibModal', 'refstackApiUrl', 'raiseAlert'
    ];

    /**
     * RefStack Results Report Controller
     * This controller is for the '/results/<test run ID>' page where a user can
     * view details for a specific test run.
     */
    function ResultsReportController($http, $stateParams, $window,
        $uibModal, refstackApiUrl, raiseAlert) {

        var ctrl = this;

        ctrl.getVersionList = getVersionList;
        ctrl.getResults = getResults;
        ctrl.isEditingAllowed = isEditingAllowed;
        ctrl.isShared = isShared;
        ctrl.shareTestRun = shareTestRun;
        ctrl.deleteTestRun = deleteTestRun;
        ctrl.updateGuidelines = updateGuidelines;
        ctrl.getTargetCapabilities = getTargetCapabilities;
        ctrl.buildCapabilityV1_2 = buildCapabilityV1_2;
        ctrl.buildCapabilityV1_3 = buildCapabilityV1_3;
        ctrl.buildCapabilitiesObject = buildCapabilitiesObject;
        ctrl.isTestFlagged = isTestFlagged;
        ctrl.getFlaggedReason = getFlaggedReason;
        ctrl.isCapabilityShown = isCapabilityShown;
        ctrl.isTestShown = isTestShown;
        ctrl.getCapabilityTestCount = getCapabilityTestCount;
        ctrl.getStatusTestCount = getStatusTestCount;
        ctrl.openFullTestListModal = openFullTestListModal;

        /** The testID extracted from the URL route. */
        ctrl.testId = $stateParams.testID;

        /** The target OpenStack marketing program to compare against. */
        ctrl.target = 'platform';

        /** Mappings of DefCore components to marketing program names. */
        ctrl.targetMappings = {
            'platform': 'Openstack Powered Platform',
            'compute': 'OpenStack Powered Compute',
            'object': 'OpenStack Powered Object Storage'
        };

        /** The schema version of the currently selected guideline data. */
        ctrl.schemaVersion = null;

        /** The selected test status used for test filtering. */
        ctrl.testStatus = 'total';

        /** The HTML template that all accordian groups will use. */
        ctrl.detailsTemplate = 'components/results-report/partials/' +
                               'reportDetails.html';

        /**
         * Retrieve an array of available guideline files from the Refstack
         * API server, sort this array reverse-alphabetically, and store it in
         * a scoped variable. The scope's selected version is initialized to
         * the latest (i.e. first) version here as well. After a successful API
         * call, the function to update the capabilities is called.
         * Sample API return array: ["2015.03.json", "2015.04.json"]
         */
        function getVersionList() {
            var content_url = refstackApiUrl + '/guidelines';
            ctrl.versionsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.versionList = data.sort().reverse();
                    if (!ctrl.version) {
                        // Default to the first approved guideline which is
                        // expected to be at index 1.
                        ctrl.version = ctrl.versionList[1];
                    }
                    ctrl.updateGuidelines();
                }).error(function (error) {
                    ctrl.showError = true;
                    ctrl.error = 'Error retrieving version list: ' +
                        angular.toJson(error);
                });
        }

        /**
         * Retrieve results from the Refstack API server based on the test
         * run id in the URL. This function is the first function that will
         * be called from the controller. Upon successful retrieval of results,
         * the function that gets the version list will be called.
         */
        function getResults() {
            var content_url = refstackApiUrl + '/results/' + ctrl.testId;
            ctrl.resultsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.resultsData = data;
                    ctrl.version = ctrl.resultsData.meta.guideline;
                    if (ctrl.resultsData.meta.target) {
                        ctrl.target = ctrl.resultsData.meta.target;
                    }
                    getVersionList();
                }).error(function (error) {
                    ctrl.showError = true;
                    ctrl.resultsData = null;
                    ctrl.error = 'Error retrieving results from server: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This tells you whether the current results can be edited/managed
         * based on if the current user is the owner of the results set.
         * @returns {Boolean} true if editing is allowed
         */
        function isEditingAllowed() {
            return Boolean(ctrl.resultsData &&
                ctrl.resultsData.user_role === 'owner');
        }
        /**
         * This tells you whether the current results are shared with the
         * community or not.
         * @returns {Boolean} true if the results are shared
         */
        function isShared() {
            return Boolean(ctrl.resultsData &&
                'shared' in ctrl.resultsData.meta);
        }

        /**
         * This will send an API request in order to share or unshare the
         * current results based on the passed in shareState.
         * @param {Boolean} shareState - Whether to share or unshare results.
         */
        function shareTestRun(shareState) {
            var content_url = [
                refstackApiUrl, '/results/', ctrl.testId, '/meta/shared'
            ].join('');
            if (shareState) {
                ctrl.shareRequest =
                    $http.post(content_url, 'true').success(function () {
                        ctrl.resultsData.meta.shared = 'true';
                        raiseAlert('success', '', 'Test run shared!');
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            } else {
                ctrl.shareRequest =
                    $http.delete(content_url).success(function () {
                        delete ctrl.resultsData.meta.shared;
                        raiseAlert('success', '', 'Test run unshared!');
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            }
        }

        /**
         * This will send a request to the API to delete the current
         * test results set.
         */
        function deleteTestRun() {
            var content_url = [
                refstackApiUrl, '/results/', ctrl.testId
            ].join('');
            ctrl.deleteRequest =
                $http.delete(content_url).success(function () {
                    $window.history.back();
                }).error(function (error) {
                    raiseAlert('danger', error.title, error.detail);
                });
        }

        /**
         * This will contact the Refstack API server to retrieve the JSON
         * content of the guideline file corresponding to the selected
         * version. A function to construct an object from the capability
         * data will be called upon successful retrieval.
         */
        function updateGuidelines() {
            ctrl.guidelineData = null;
            ctrl.showError = false;
            var content_url = refstackApiUrl + '/guidelines/' +
                ctrl.version;
            ctrl.capsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.guidelineData = data;
                    ctrl.schemaVersion = data.schema;
                    ctrl.buildCapabilitiesObject();
                }).error(function (error) {
                    ctrl.showError = true;
                    ctrl.guidelineData = null;
                    ctrl.error = 'Error retrieving guideline date: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This will get all the capabilities relevant to the target and
         * their corresponding statuses.
         * @returns {Object} Object containing each capability and their status
         */
        function getTargetCapabilities() {
            var components = ctrl.guidelineData.components;
            var targetCaps = {};

            // The 'platform' target is comprised of multiple components, so
            // we need to get the capabilities belonging to each of its
            // components.
            if (ctrl.target === 'platform') {
                var platform_components =
                    ctrl.guidelineData.platform.required;

                // This will contain status priority values, where lower
                // values mean higher priorities.
                var statusMap = {
                    required: 1,
                    advisory: 2,
                    deprecated: 3,
                    removed: 4
                };

                // For each component required for the platform program.
                angular.forEach(platform_components, function (component) {
                    // Get each capability list belonging to each status.
                    angular.forEach(components[component],
                        function (caps, status) {
                            // For each capability.
                            angular.forEach(caps, function(cap) {
                                // If the capability has already been added.
                                if (cap in targetCaps) {
                                    // If the status priority value is less
                                    // than the saved priority value, update
                                    // the value.
                                    if (statusMap[status] <
                                        statusMap[targetCaps[cap]]) {
                                        targetCaps[cap] = status;
                                    }
                                }
                                else {
                                    targetCaps[cap] = status;
                                }
                            });
                        });
                });
            }
            else {
                angular.forEach(components[ctrl.target],
                    function (caps, status) {
                        angular.forEach(caps, function(cap) {
                            targetCaps[cap] = status;
                        });
                    });
            }
            return targetCaps;
        }

        /**
         * This will build the a capability object for schema version 1.2.
         * This object will contain the information needed to form a report in
         * the HTML template.
         * @param {String} capId capability ID
         */
        function buildCapabilityV1_2(capId) {
            var cap = {
                'id': capId,
                'passedTests': [],
                'notPassedTests': [],
                'passedFlagged': [],
                'notPassedFlagged': []
            };
            var capDetails = ctrl.guidelineData.capabilities[capId];
            // Loop through each test belonging to the capability.
            angular.forEach(capDetails.tests,
                function (testId) {
                    // If the test ID is in the results' test list, add
                    // it to the passedTests array.
                    if (ctrl.resultsData.results.indexOf(testId) > -1) {
                        cap.passedTests.push(testId);
                        if (capDetails.flagged.indexOf(testId) > -1) {
                            cap.passedFlagged.push(testId);
                        }
                    }
                    else {
                        cap.notPassedTests.push(testId);
                        if (capDetails.flagged.indexOf(testId) > -1) {
                            cap.notPassedFlagged.push(testId);
                        }
                    }
                });
            return cap;
        }

        /**
         * This will build the a capability object for schema version 1.3 and
         * above. This object will contain the information needed to form a
         * report in the HTML template.
         * @param {String} capId capability ID
         */
        function buildCapabilityV1_3(capId) {
            var cap = {
                'id': capId,
                'passedTests': [],
                'notPassedTests': [],
                'passedFlagged': [],
                'notPassedFlagged': []
            };
            // Loop through each test belonging to the capability.
            angular.forEach(ctrl.guidelineData.capabilities[capId].tests,
                function (details, testId) {
                    var passed = false;

                    // If the test ID is in the results' test list.
                    if (ctrl.resultsData.results.indexOf(testId) > -1) {
                        passed = true;
                    }
                    else if ('aliases' in details) {
                        var len = details.aliases.length;
                        for (var i = 0; i < len; i++) {
                            var alias = details.aliases[i];
                            if (ctrl.resultsData.results.indexOf(alias) > -1) {
                                passed = true;
                                break;
                            }
                        }
                    }

                    // Add to correct array based on whether the test was
                    // passed or not.
                    if (passed) {
                        cap.passedTests.push(testId);
                        if ('flagged' in details) {
                            cap.passedFlagged.push(testId);
                        }
                    }
                    else {
                        cap.notPassedTests.push(testId);
                        if ('flagged' in details) {
                            cap.notPassedFlagged.push(testId);
                        }
                    }
                });
            return cap;
        }

        /**
         * This will check the schema version of the current capabilities file,
         * and will call the correct method to build an object based on the
         * capability data retrieved from the Refstack API server.
         */
        function buildCapabilitiesObject() {
            // This is the object template where 'count' is the number of
            // total tests that fall under the given status, and 'passedCount'
            // is the number of tests passed. The 'caps' array will contain
            // objects with details regarding each capability.
            ctrl.caps = {
                'required': {'caps': [], 'count': 0, 'passedCount': 0,
                        'flagFailCount': 0, 'flagPassCount': 0},
                'advisory': {'caps': [], 'count': 0, 'passedCount': 0,
                        'flagFailCount': 0, 'flagPassCount': 0},
                'deprecated': {'caps': [], 'count': 0, 'passedCount': 0,
                          'flagFailCount': 0, 'flagPassCount': 0},
                'removed': {'caps': [], 'count': 0, 'passedCount': 0,
                       'flagFailCount': 0, 'flagPassCount': 0}
            };

            switch (ctrl.schemaVersion) {
                case '1.2':
                    var capMethod = 'buildCapabilityV1_2';
                    break;
                case '1.3':
                case '1.4':
                case '1.5':
                    capMethod = 'buildCapabilityV1_3';
                    break;
                default:
                    ctrl.showError = true;
                    ctrl.guidelineData = null;
                    ctrl.error = 'The schema version for the guideline ' +
                         'file selected (' + ctrl.schemaVersion +
                         ') is currently not supported.';
                    return;
            }

            // Get test details for each relevant capability and store
            // them in the scope's 'caps' object.
            var targetCaps = ctrl.getTargetCapabilities();
            angular.forEach(targetCaps, function(status, capId) {
                var cap = ctrl[capMethod](capId);
                ctrl.caps[status].count +=
                    cap.passedTests.length + cap.notPassedTests.length;
                ctrl.caps[status].passedCount += cap.passedTests.length;
                ctrl.caps[status].flagPassCount += cap.passedFlagged.length;
                ctrl.caps[status].flagFailCount +=
                    cap.notPassedFlagged.length;
                ctrl.caps[status].caps.push(cap);
            });

            ctrl.requiredPassPercent = (ctrl.caps.required.passedCount *
                100 / ctrl.caps.required.count);

            ctrl.totalRequiredFailCount = ctrl.caps.required.count -
                ctrl.caps.required.passedCount;
            ctrl.totalRequiredFlagCount =
                ctrl.caps.required.flagFailCount +
                ctrl.caps.required.flagPassCount;
            ctrl.totalNonFlagCount = ctrl.caps.required.count -
                ctrl.totalRequiredFlagCount;
            ctrl.nonFlagPassCount = ctrl.totalNonFlagCount -
                (ctrl.totalRequiredFailCount -
                 ctrl.caps.required.flagFailCount);

            ctrl.nonFlagRequiredPassPercent = (ctrl.nonFlagPassCount *
                100 / ctrl.totalNonFlagCount);
        }

        /**
         * This will check if a given test is flagged.
         * @param {String} test ID of the test to check
         * @param {Object} capObj capability that test is under
         * @returns {Boolean} truthy value if test is flagged
         */
        function isTestFlagged(test, capObj) {
            if (!capObj) {
                return false;
            }
            return (((ctrl.schemaVersion === '1.2') &&
                (capObj.flagged.indexOf(test) > -1)) ||
                    ((ctrl.schemaVersion >= '1.3') &&
                (capObj.tests[test].flagged)));
        }

        /**
         * This will return the reason a test is flagged. An empty string
         * will be returned if the passed in test is not flagged.
         * @param {String} test ID of the test to check
         * @param {String} capObj capability that test is under
         * @returns {String} reason
         */
        function getFlaggedReason(test, capObj) {
            if ((ctrl.schemaVersion === '1.2') &&
                (ctrl.isTestFlagged(test, capObj))) {

                // Return a generic message since schema 1.2 does not
                // provide flag reasons.
                return 'DefCore has flagged this test.';
            }
            else if ((ctrl.schemaVersion >= '1.3') &&
                (ctrl.isTestFlagged(test, capObj))) {

                return capObj.tests[test].flagged.reason;
            }
            else {
                return '';
            }
        }

        /**
         * This will check the if a capability should be shown based on the
         * test filter selected. If a capability does not have any tests
         * belonging under the given filter, it should not be shown.
         * @param {Object} capability Built object for capability
         * @returns {Boolean} true if capability should be shown
         */
        function isCapabilityShown(capability) {
            return ((ctrl.testStatus === 'total') ||
               (ctrl.testStatus === 'passed' &&
                capability.passedTests.length > 0) ||
               (ctrl.testStatus === 'not passed' &&
                capability.notPassedTests.length > 0) ||
               (ctrl.testStatus === 'flagged' &&
                (capability.passedFlagged.length +
                 capability.notPassedFlagged.length > 0)));
        }

        /**
         * This will check the if a test should be shown based on the test
         * filter selected.
         * @param {String} test ID of the test
         * @param {Object} capability Built object for capability
         * @return {Boolean} true if test should be shown
         */
        function isTestShown(test, capability) {
            return ((ctrl.testStatus === 'total') ||
                (ctrl.testStatus === 'passed' &&
                 capability.passedTests.indexOf(test) > -1) ||
                (ctrl.testStatus === 'not passed' &&
                 capability.notPassedTests.indexOf(test) > -1) ||
                (ctrl.testStatus === 'flagged' &&
                 (capability.passedFlagged.indexOf(test) > -1 ||
                  capability.notPassedFlagged.indexOf(test) > -1)));
        }

        /**
         * This will give the number of tests belonging under the selected
         * test filter for a given capability.
         * @param {Object} capability Built object for capability
         * @returns {Number} number of tests under filter
         */
        function getCapabilityTestCount(capability) {
            if (ctrl.testStatus === 'total') {
                return capability.passedTests.length +
                   capability.notPassedTests.length;
            }
            else if (ctrl.testStatus === 'passed') {
                return capability.passedTests.length;
            }
            else if (ctrl.testStatus === 'not passed') {
                return capability.notPassedTests.length;
            }
            else if (ctrl.testStatus === 'flagged') {
                return capability.passedFlagged.length +
                   capability.notPassedFlagged.length;
            }
            else {
                return 0;
            }
        }

        /**
         * This will give the number of tests belonging under the selected
         * test filter for a given status.
         * @param {String} capability status
         * @returns {Number} number of tests for status under filter
         */
        function getStatusTestCount(status) {
            if (!ctrl.caps) {
                return -1;
            }
            else if (ctrl.testStatus === 'total') {
                return ctrl.caps[status].count;
            }
            else if (ctrl.testStatus === 'passed') {
                return ctrl.caps[status].passedCount;
            }
            else if (ctrl.testStatus === 'not passed') {
                return ctrl.caps[status].count -
                  ctrl.caps[status].passedCount;
            }
            else if (ctrl.testStatus === 'flagged') {
                return ctrl.caps[status].flagFailCount +
                  ctrl.caps[status].flagPassCount;
            }
            else {
                return -1;
            }
        }

        /**
         * This will open the modal that will show the full list of passed
         * tests for the current results.
         */
        function openFullTestListModal() {
            $uibModal.open({
                templateUrl: '/components/results-report/partials' +
                        '/fullTestListModal.html',
                backdrop: true,
                windowClass: 'modal',
                animation: true,
                controller: 'FullTestListModalController as modal',
                size: 'lg',
                resolve: {
                    tests: function () {
                        return ctrl.resultsData.results;
                    }
                }
            });
        }

        getResults();
    }

    angular
        .module('refstackApp')
        .controller('FullTestListModalController', FullTestListModalController);

    FullTestListModalController.$inject = ['$uibModalInstance', 'tests'];

    /**
     * Full Test List Modal Controller
     * This controller is for the modal that appears if a user wants to see the
     * full list of passed tests on a report page.
     */
    function FullTestListModalController($uibModalInstance, tests) {
        var ctrl = this;

        ctrl.tests = tests;

        /**
         * This function will close/dismiss the modal.
         */
        ctrl.close = function () {
            $uibModalInstance.dismiss('exit');
        };

        /**
         * This function will return a string representing the sorted
         * tests list separated by newlines.
         */
        ctrl.getTestListString = function () {
            return ctrl.tests.sort().join('\n');
        };
    }
})();
