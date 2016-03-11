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
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = [
        '$scope', '$http', '$filter', '$state', 'refstackApiUrl','raiseAlert'
    ];

    /**
     * RefStack Results Controller
     * This controller is for the '/results' page where a user can browse
     * a listing of community uploaded results.
     */
    function ResultsController($scope, $http, $filter, $state, refstackApiUrl,
        raiseAlert) {
        var ctrl = this;

        ctrl.update = update;
        ctrl.open = open;
        ctrl.clearFilters = clearFilters;
        ctrl.associateMeta = associateMeta;
        ctrl.getVersionList = getVersionList;

        /** Mappings of DefCore components to marketing program names. */
        ctrl.targetMappings = {
            'platform': 'Openstack Powered Platform',
            'compute': 'OpenStack Powered Compute',
            'object': 'OpenStack Powered Object Storage'
        };

        /** Initial page to be on. */
        ctrl.currentPage = 1;

        /**
         * How many results should display on each page. Since pagination
         * is server-side implemented, this value should match the
         * 'results_per_page' configuration of the Refstack server which
         * defaults to 20.
         */
        ctrl.itemsPerPage = 20;

        /**
         * How many page buttons should be displayed at max before adding
         * the '...' button.
         */
        ctrl.maxSize = 5;

        /** The upload date lower limit to be used in filtering results. */
        ctrl.startDate = '';

        /** The upload date upper limit to be used in filtering results. */
        ctrl.endDate = '';

        /** The date format for the date picker. */
        ctrl.format = 'yyyy-MM-dd';

        /** Check to see if this page should display user-specific results. */
        ctrl.isUserResults = $state.current.name === 'userResults';

        // Should only be on user-results-page if authenticated.
        if (ctrl.isUserResults && !$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.pageHeader = ctrl.isUserResults ?
            'Private test results' : 'Community test results';

        ctrl.pageParagraph = ctrl.isUserResults ?
            'Your most recently uploaded test results are listed here.' :
            'The most recently uploaded community test results are listed ' +
            'here.';

        if (ctrl.isUserResults) {
            ctrl.authRequest = $scope.auth.doSignCheck()
                .then(ctrl.update);
        } else {
            ctrl.update();
        }

        /**
         * This will contact the Refstack API to get a listing of test run
         * results.
         */
        function update() {
            ctrl.showError = false;
            // Construct the API URL based on user-specified filters.
            var content_url = refstackApiUrl + '/results' +
                '?page=' + ctrl.currentPage;
            var start = $filter('date')(ctrl.startDate, 'yyyy-MM-dd');
            if (start) {
                content_url =
                    content_url + '&start_date=' + start + ' 00:00:00';
            }
            var end = $filter('date')(ctrl.endDate, 'yyyy-MM-dd');
            if (end) {
                content_url = content_url + '&end_date=' + end + ' 23:59:59';
            }
            if (ctrl.isUserResults) {
                content_url = content_url + '&signed';
            }
            ctrl.resultsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.data = data;
                    ctrl.totalItems = ctrl.data.pagination.total_pages *
                        ctrl.itemsPerPage;
                    ctrl.currentPage = ctrl.data.pagination.current_page;
                }).error(function (error) {
                    ctrl.data = null;
                    ctrl.totalItems = 0;
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving results listing from server: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This is called when the date filter calendar is opened. It
         * does some event handling, and sets a scope variable so the UI
         * knows which calendar was opened.
         * @param {Object} $event - The Event object
         * @param {String} openVar - Tells which calendar was opened
         */
        function open($event, openVar) {
            $event.preventDefault();
            $event.stopPropagation();
            ctrl[openVar] = true;
        }

        /**
         * This function will clear all filters and update the results
         * listing.
         */
        function clearFilters() {
            ctrl.startDate = null;
            ctrl.endDate = null;
            ctrl.update();
        }

        /**
         * This will send an API request in order to associate a metadata
         * key-value pair with the given testId
         * @param {Number} index - index of the test object in the results list
         * @param {String} key - metadata key
         * @param {String} value - metadata value
         */
        function associateMeta(index, key, value) {
            var testId = ctrl.data.results[index].id;
            var metaUrl = [
                refstackApiUrl, '/results/', testId, '/meta/', key
            ].join('');

            var editFlag = key + 'Edit';
            if (value) {
                ctrl.associateRequest = $http.post(metaUrl, value)
                    .success(function () {
                        ctrl.data.results[index][editFlag] = false;
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            }
            else {
                ctrl.unassociateRequest = $http.delete(metaUrl)
                    .success(function () {
                        ctrl.data.results[index][editFlag] = false;
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            }
        }

        /**
         * Retrieve an array of available capability files from the Refstack
         * API server, sort this array reverse-alphabetically, and store it in
         * a scoped variable.
         * Sample API return array: ["2015.03.json", "2015.04.json"]
         */
        function getVersionList() {
            if (ctrl.versionList) {
                return;
            }
            var content_url = refstackApiUrl + '/guidelines';
            ctrl.versionsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.versionList = data.sort().reverse();
                }).error(function (error) {
                    raiseAlert('danger', error.title,
                               'Unable to retrieve version list');
                });
        }

    }
})();
