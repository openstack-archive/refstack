var refstackApp = angular.module('refstackApp');

/**
 * Refstack Results Report Controller
 * This controller is for the '/results/<test run ID>' page where a user can
 * view details for a specific test run.
 */
refstackApp.controller('resultsReportController',
    ['$scope', '$http', '$stateParams',
     '$window', '$modal', 'refstackApiUrl', 'raiseAlert',
     function ($scope, $http, $stateParams, $window, $modal,
               refstackApiUrl, raiseAlert) {
         'use strict';

         /** The testID extracted from the URL route. */
         $scope.testId = $stateParams.testID;

         /** Whether to hide tests on start.*/
         $scope.hideTests = true;

         /** The target OpenStack marketing program to compare against. */
         $scope.target = 'platform';

         /** Mappings of DefCore components to marketing program names. */
         $scope.targetMappings = {
             'platform': 'Openstack Powered Platform',
             'compute': 'OpenStack Powered Compute',
             'object': 'OpenStack Powered Object Storage'
         };

         /** The schema version of the currently selected capabilities data. */
         $scope.schemaVersion = null;

         /** The selected test status used for test filtering. */
         $scope.testStatus = 'all';

         /** The HTML template that all accordian groups will use. */
         $scope.detailsTemplate = 'components/results-report/partials/' +
                                  'reportDetails.html';

         /**
          * Retrieve an array of available capability files from the Refstack
          * API server, sort this array reverse-alphabetically, and store it in
          * a scoped variable. The scope's selected version is initialized to
          * the latest (i.e. first) version here as well. After a successful API
          * call, the function to update the capabilities is called.
          * Sample API return array: ["2015.03.json", "2015.04.json"]
          */
         var getVersionList = function () {
             var content_url = refstackApiUrl + '/capabilities';
             $scope.versionsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.versionList = data.sort().reverse();
                     $scope.version = $scope.versionList[0];
                     $scope.updateCapabilities();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.error = 'Error retrieving version list: ' +
                         JSON.stringify(error);
                 });
         };

         /**
          * Retrieve results from the Refstack API server based on the test
          * run id in the URL. This function is the first function that will
          * be called from the controller. Upon successful retrieval of results,
          * the function that gets the version list will be called.
          */
         var getResults = function () {
             var content_url = refstackApiUrl + '/results/' + $scope.testId;
             $scope.resultsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.resultsData = data;
                     getVersionList();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.resultsData = null;
                     $scope.error = 'Error retrieving results from server: ' +
                         JSON.stringify(error);

                 });
         };

         $scope.isEditingAllowed = function () {
             return Boolean($scope.resultsData &&
                 $scope.resultsData.user_role === 'owner');
         };

         $scope.isShared = function () {
             return Boolean($scope.resultsData &&
                 'shared' in $scope.resultsData.meta);
         };

         $scope.shareTestRun = function (shareState) {
             var content_url = [
                 refstackApiUrl, '/results/', $scope.testId, '/meta/shared'
             ].join('');
             if (shareState) {
                 $scope.shareRequest =
                     $http.post(content_url, 'true').success(function () {
                         $scope.resultsData.meta.shared = 'true';
                         raiseAlert('success', '', 'Test run shared!');
                     }).error(function (error) {
                         raiseAlert('danger',
                             error.title, error.detail);
                     });
             } else {
                 $scope.shareRequest =
                     $http.delete(content_url).success(function () {
                         delete $scope.resultsData.meta.shared;
                         raiseAlert('success', '', 'Test run unshared!');
                     }).error(function (error) {
                         raiseAlert('danger',
                             error.title, error.detail);
                     });
             }
         };

         $scope.deleteTestRun = function () {
             var content_url = [
                 refstackApiUrl, '/results/', $scope.testId
             ].join('');
             $scope.deleteRequest =
                 $http.delete(content_url).success(function () {
                     $window.history.back();
                 }).error(function (error) {
                     raiseAlert('danger',
                         error.title, error.detail);
                 });
         };

         /**
          * This will contact the Refstack API server to retrieve the JSON
          * content of the capability file corresponding to the selected
          * version. A function to construct an object from the capability
          * date will be called upon successful retrieval.
          */
         $scope.updateCapabilities = function () {
             $scope.capabilityData = null;
             $scope.showError = false;
             var content_url = refstackApiUrl + '/capabilities/' +
                 $scope.version;
             $scope.capsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.capabilityData = data;
                     $scope.schemaVersion = data.schema;
                     $scope.buildCapabilitiesObject();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.capabilityData = null;
                     $scope.error = 'Error retrieving capabilities: ' +
                         JSON.stringify(error);
                 });
         };

         /**
          * This will get all the capabilities relevant to the target and
          * their corresponding statuses.
          * @returns {Object} Object containing each capability and their status
          */
         $scope.getTargetCapabilities = function () {
             var components = $scope.capabilityData.components;
             var targetCaps = {};

             // The 'platform' target is comprised of multiple components, so
             // we need to get the capabilities belonging to each of its
             // components.
             if ($scope.target === 'platform') {
                 var platform_components =
                     $scope.capabilityData.platform.required;

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
                 angular.forEach(components[$scope.target],
                     function (caps, status) {
                         angular.forEach(caps, function(cap) {
                             targetCaps[cap] = status;
                         });
                     });
             }
             return targetCaps;
         };

         /**
          * This will build the a capability object for schema version 1.2.
          * This object will contain the information needed to form a report in
          * the HTML template.
          * @param {String} capId capability ID
          */
         $scope.buildCapabilityV1_2 = function (capId) {
             var cap = {
                 'id': capId,
                 'passedTests': [],
                 'notPassedTests': [],
                 'passedFlagged': [],
                 'notPassedFlagged': []
             };
             var capDetails = $scope.capabilityData.capabilities[capId];
             // Loop through each test belonging to the capability.
             angular.forEach(capDetails.tests,
                 function (testId) {
                     // If the test ID is in the results' test list, add
                     // it to the passedTests array.
                     if ($scope.resultsData.results.indexOf(testId) > -1) {
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
         };

         /**
          * This will build the a capability object for schema version 1.3.
          * This object will contain the information needed to form a report in
          * the HTML template.
          * @param {String} capId capability ID
          */
         $scope.buildCapabilityV1_3 = function (capId) {
             var cap = {
                 'id': capId,
                 'passedTests': [],
                 'notPassedTests': [],
                 'passedFlagged': [],
                 'notPassedFlagged': []
             };
             // Loop through each test belonging to the capability.
             angular.forEach($scope.capabilityData.capabilities[capId].tests,
                 function (details, testId) {
                     // If the test ID is in the results' test list, add
                     // it to the passedTests array.
                     if ($scope.resultsData.results.indexOf(testId) > -1) {
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
         };

         /**
          * This will check the schema version of the current capabilities file,
          * and will call the correct method to build an object based on the
          * capability data retrieved from the Refstack API server.
          */
         $scope.buildCapabilitiesObject = function () {
             // This is the object template where 'count' is the number of
             // total tests that fall under the given status, and 'passedCount'
             // is the number of tests passed. The 'caps' array will contain
             // objects with details regarding each capability.
             $scope.caps = {
                 'required': {'caps': [], 'count': 0, 'passedCount': 0,
                              'flagFailCount': 0, 'flagPassCount': 0},
                 'advisory': {'caps': [], 'count': 0, 'passedCount': 0,
                              'flagFailCount': 0, 'flagPassCount': 0},
                 'deprecated': {'caps': [], 'count': 0, 'passedCount': 0,
                                'flagFailCount': 0, 'flagPassCount': 0},
                 'removed': {'caps': [], 'count': 0, 'passedCount': 0,
                             'flagFailCount': 0, 'flagPassCount': 0}
             };

             switch ($scope.schemaVersion) {
                 case '1.2':
                     var capMethod = 'buildCapabilityV1_2';
                     break;
                 case '1.3':
                     capMethod = 'buildCapabilityV1_3';
                     break;
                 default:
                     $scope.showError = true;
                     $scope.capabilityData = null;
                     $scope.error = 'The schema version for the capabilities ' +
                                    'file selected (' + $scope.schemaVersion +
                                    ') is currently not supported.';
                     return;
             }

             // Get test details for each relevant capability and store
             // them in the scope's 'caps' object.
             var targetCaps = $scope.getTargetCapabilities();
             angular.forEach(targetCaps, function(status, capId) {
                 var cap = $scope[capMethod](capId);
                 $scope.caps[status].count +=
                     cap.passedTests.length + cap.notPassedTests.length;
                 $scope.caps[status].passedCount += cap.passedTests.length;
                 $scope.caps[status].flagPassCount += cap.passedFlagged.length;
                 $scope.caps[status].flagFailCount +=
                     cap.notPassedFlagged.length;
                 $scope.caps[status].caps.push(cap);
             });

             $scope.requiredPassPercent = ($scope.caps.required.passedCount *
                 100 / $scope.caps.required.count);

             $scope.totalRequiredFailCount = $scope.caps.required.count -
                 $scope.caps.required.passedCount;
             $scope.totalRequiredFlagCount =
                 $scope.caps.required.flagFailCount +
                 $scope.caps.required.flagPassCount;
             $scope.totalNonFlagCount = $scope.caps.required.count -
                 $scope.totalRequiredFlagCount;
             $scope.nonFlagPassCount = $scope.totalNonFlagCount -
                 ($scope.totalRequiredFailCount -
                  $scope.caps.required.flagFailCount);

             $scope.nonFlagRequiredPassPercent = ($scope.nonFlagPassCount *
                 100 / $scope.totalNonFlagCount);
         };

         /**
          * This will check if a given test is flagged.
          * @param {String} test ID of the test to check
          * @param {Object} capObj capability that test is under
          * @returns {Boolean} truthy value if test is flagged
          */
         $scope.isTestFlagged = function (test, capObj) {
             if (!capObj) {
                 return false;
             }
             return ((($scope.schemaVersion === '1.2') &&
                      (capObj.flagged.indexOf(test) > -1)) ||
                     (($scope.schemaVersion === '1.3') &&
                      (capObj.tests[test].flagged)));
         };

         /**
          * This will return the reason a test is flagged. An empty string
          * will be returned if the passed in test is not flagged.
          * @param {String} test ID of the test to check
          * @param {String} capObj capability that test is under
          * @returns {String} reason
          */
         $scope.getFlaggedReason = function (test, capObj) {
             if (($scope.schemaVersion === '1.2') &&
                 ($scope.isTestFlagged(test, capObj))){

                 // Return a generic message since schema 1.2 does not
                 // provide flag reasons.
                 return 'DefCore has flagged this test.';
             }
             else if (($scope.schemaVersion === '1.3') &&
                      ($scope.isTestFlagged(test, capObj))){

                 return capObj.tests[test].flagged.reason;
             }
             else {
                 return '';
             }
         };

         /**
          * This will check the if a capability should be shown based on the
          * test filter selected. If a capability does not have any tests
          * belonging under the given filter, it should not be shown.
          * @param {Object} capability Built object for capability
          * @returns {Boolean} true if capability should be shown
          */
         $scope.isCapabilityShown = function (capability) {
             return (($scope.testStatus === 'all') ||
                ($scope.testStatus === 'passed' &&
                 capability.passedTests.length > 0) ||
                ($scope.testStatus === 'failed' &&
                 capability.notPassedTests.length > 0) ||
                ($scope.testStatus === 'flagged' &&
                 (capability.passedFlagged.length +
                  capability.notPassedFlagged.length > 0)));
         };

         /**
          * This will check the if a test should be shown based on the test
          * filter selected.
          * @param {String} test ID of the test
          * @param {Object} capability Built object for capability
          * @return {Boolean} true if test should be shown
          */
         $scope.isTestShown = function (test, capability) {
             return (($scope.testStatus === 'all') ||
                 ($scope.testStatus === 'passed' &&
                  capability.passedTests.indexOf(test) > -1) ||
                 ($scope.testStatus === 'failed' &&
                  capability.notPassedTests.indexOf(test) > -1) ||
                 ($scope.testStatus === 'flagged' &&
                  (capability.passedFlagged.indexOf(test) > -1 ||
                   capability.notPassedFlagged.indexOf(test) > -1)));
         };

         /**
          * This will give the number of tests belonging under the selected
          * test filter.
          * @param {Object} capability Built object for capability
          * @returns {Number} number of tests under filter
          */
         $scope.getTestCount = function (capability) {
             if ($scope.testStatus === 'all') {
                 return capability.passedTests.length +
                    capability.notPassedTests.length;
             }
             else if ($scope.testStatus === 'passed') {
                 return capability.passedTests.length;
             }
             else if ($scope.testStatus === 'failed') {
                 return capability.notPassedTests.length;
             }
             else if ($scope.testStatus === 'flagged') {
                 return capability.passedFlagged.length +
                    capability.notPassedFlagged.length;
             }
             else {
                 return 0;
             }
         };

         $scope.openFullTestListModal = function () {
             $modal.open({
                 templateUrl: '/components/results-report/partials' +
                              '/fullTestListModal.html',
                 backdrop: true,
                 windowClass: 'modal',
                 animation: true,
                 controller: 'fullTestListModalController',
                 size: 'lg',
                 resolve: {
                     tests: function () {
                         return $scope.resultsData.results;
                     }
                 }
             });
         };

         getResults();
     }
    ]
);


/**
 * Full Test List Modal Controller
 * This controller is for the modal that appears if a user wants to see the
 * full list of passed tests on a report page.
 */
refstackApp.controller('fullTestListModalController',
    ['$scope', '$modalInstance', 'tests',
     function ($scope, $modalInstance, tests) {
         'use strict';

         $scope.tests = tests;

         /**
          * This function will close/dismiss the modal.
          */
         $scope.close = function () {
             $modalInstance.dismiss('exit');
         };

         /**
          * This function will return a string representing the sorted
          * tests list separated by newlines.
          */
         $scope.getTestListString = function () {
             return $scope.tests.sort().join('\n');
         };
     }]
);
