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
        .controller('GuidelinesController', GuidelinesController);

    GuidelinesController.$inject = ['$http', '$uibModal', 'refstackApiUrl'];

    /**
     * RefStack Guidelines Controller
     * This controller is for the '/guidelines' page where a user can browse
     * through tests belonging to DefCore-defined capabilities.
     */
    function GuidelinesController($http, $uibModal, refstackApiUrl) {
        var ctrl = this;

        ctrl.getVersionList = getVersionList;
        ctrl.update = update;
        ctrl.updateTargetCapabilities = updateTargetCapabilities;
        ctrl.filterStatus = filterStatus;
        ctrl.getObjectLength = getObjectLength;
        ctrl.getTestList = getTestList;
        ctrl.openTestListModal = openTestListModal;

        /** The target OpenStack marketing program to show capabilities for. */
        ctrl.target = 'platform';

        /** The various possible capability statuses. */
        ctrl.status = {
            required: true,
            advisory: false,
            deprecated: false,
            removed: false
        };

        /**
         * The template to load for displaying capability details.
         */
        ctrl.detailsTemplate = 'components/guidelines/partials/' +
                               'guidelineDetails.html';

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
                    ctrl.version = ctrl.versionList[0];
                    ctrl.update();
                }).error(function (error) {
                    ctrl.showError = true;
                    ctrl.error = 'Error retrieving version list: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This will contact the Refstack API server to retrieve the JSON
         * content of the guideline file corresponding to the selected
         * version.
         */
        function update() {
            var content_url = refstackApiUrl + '/guidelines/' + ctrl.version;
            ctrl.capsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.guidelines = data;
                    ctrl.updateTargetCapabilities();
                }).error(function (error) {
                    ctrl.showError = true;
                    ctrl.guidelines = null;
                    ctrl.error = 'Error retrieving guideline content: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This will update the scope's 'targetCapabilities' object with
         * capabilities belonging to the selected OpenStack marketing program
         * (programs typically correspond to 'components' in the DefCore
         * schema). Each capability will have its status mapped to it.
         */
        function updateTargetCapabilities() {
            ctrl.targetCapabilities = {};
            var components = ctrl.guidelines.components;
            var targetCaps = ctrl.targetCapabilities;

            // The 'platform' target is comprised of multiple components, so
            // we need to get the capabilities belonging to each of its
            // components.
            if (ctrl.target === 'platform') {
                var platform_components = ctrl.guidelines.platform.required;

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
        }

        /**
         * This filter will check if a capability's status corresponds
         * to a status that is checked/selected in the UI. This filter
         * is meant to be used with the ng-repeat directive.
         * @param {Object} capability
         * @returns {Boolean} True if capability's status is selected
         */
        function filterStatus(capability) {
            var caps = ctrl.targetCapabilities;
            return (ctrl.status.required &&
                caps[capability.id] === 'required') ||
                (ctrl.status.advisory &&
                caps[capability.id] === 'advisory') ||
                (ctrl.status.deprecated &&
                caps[capability.id] === 'deprecated') ||
                (ctrl.status.removed &&
                caps[capability.id] === 'removed');
        }

        /**
         * This function will get the length of an Object/dict based on
         * the number of keys it has.
         * @param {Object} object
         * @returns {Number} length of object
         */
        function getObjectLength(object) {
            return Object.keys(object).length;
        }

        /**
         * This will give a list of tests belonging to capabilities with
         * the selected status(es).
         */
        function getTestList() {
            var caps = ctrl.guidelines.capabilities;
            var tests = [];
            angular.forEach(ctrl.targetCapabilities,
                function (status, cap) {
                    if (ctrl.status[status]) {
                        if (ctrl.guidelines.schema === '1.2') {
                            tests.push.apply(tests, caps[cap].tests);
                        }
                        else {
                            angular.forEach(caps[cap].tests,
                                function(info, test) {
                                    tests.push(test);
                                });
                        }
                    }
                });
            return tests;
        }

        /**
         * This will open the modal that will show a list of all tests
         * belonging to capabilities with the selected status(es).
         */
        function openTestListModal() {
            $uibModal.open({
                templateUrl: '/components/guidelines/partials' +
                        '/testListModal.html',
                backdrop: true,
                windowClass: 'modal',
                animation: true,
                controller: 'TestListModalController as modal',
                size: 'lg',
                resolve: {
                    tests: function () {
                        return ctrl.getTestList();
                    },
                    version: function () {
                        return ctrl.version.slice(0, -5);
                    },
                    status: function () {
                        return ctrl.status;
                    }
                }
            });
        }

        ctrl.getVersionList();
    }

    angular
        .module('refstackApp')
        .controller('TestListModalController', TestListModalController);

    TestListModalController.$inject = [
        '$uibModalInstance', '$window', 'tests', 'version', 'status'
    ];

    /**
     * Test List Modal Controller
     * This controller is for the modal that appears if a user wants to see the
     * test list corresponding to DefCore capabilities with the selected
     * statuses.
     */
    function TestListModalController($uibModalInstance, $window, tests,
        version, status) {

        var ctrl = this;

        ctrl.tests = tests;
        ctrl.version = version;
        ctrl.status = status;
        ctrl.close = close;
        ctrl.getTestListString = getTestListString;
        ctrl.downloadTestList = downloadTestList;

        /**
         * This function will close/dismiss the modal.
         */
        function close() {
            $uibModalInstance.dismiss('exit');
        }

        /**
         * This function will return a string representing the sorted
         * tests list separated by newlines.
         */
        function getTestListString() {
            return ctrl.tests.sort().join('\n');
        }

        /**
         * Serve the test list as a downloadable file.
         */
        function downloadTestList() {
            var blob = new Blob([ctrl.getTestListString()], {type: 'text/csv'});
            var filename = ctrl.version + '-test-list.txt';
            if ($window.navigator.msSaveOrOpenBlob) {
                $window.navigator.msSaveBlob(blob, filename);
            }
            else {
                var a = $window.document.createElement('a');
                a.href = $window.URL.createObjectURL(blob);
                a.download = filename;
                $window.document.body.appendChild(a);
                a.click();
                $window.document.body.removeChild(a);
            }
        }
    }
})();
