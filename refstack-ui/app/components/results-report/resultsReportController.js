var refstackApp = angular.module('refstackApp');

/**
 * Refstack Results Report Controller
 * This controller is for the '/results/<test run ID>' page where a user can
 * view details for a specific test run.
 */
refstackApp.controller('resultsReportController',
    ['$scope', '$http', '$stateParams', 'refstackApiUrl',
     function ($scope, $http, $stateParams, refstackApiUrl) {
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
                     $scope.resultsData = null;
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
                     $scope.detailsTemplate = 'components/results-report/' +
                                              'partials/reportDetailsV' +
                                              data.schema + '.html';
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
         $scope.getTargetCapabilitites = function () {
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
          * @param {String} capID capability ID
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
          * @param {String} capID capability ID
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
                         if ('flag' in details) {
                             cap.passedFlagged.push(testId);
                         }
                     }
                     else {
                         cap.notPassedTests.push(testId);
                         if ('flag' in details) {
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
             var targetCaps = $scope.getTargetCapabilitites();
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

         getResults();
     }
    ]);
