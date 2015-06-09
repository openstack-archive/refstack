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

         /** Whether the required capabilities accordian should be open. */
         $scope.requiredOpen = true;

         /** Mappings of DefCore components to marketing program names. */
         $scope.targetMappings = {
             'platform': 'Openstack Powered Platform',
             'compute': 'OpenStack Powered Compute',
             'object': 'OpenStack Powered Object Storage'
         };

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
             $scope.showError = false;
             var content_url = refstackApiUrl + '/capabilities/' +
                 $scope.version;
             $scope.capsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.capabilityData = data;
                     $scope.buildCapabilityObject();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.capabilityData = null;
                     $scope.error = 'Error retrieving capabilities: ' +
                         JSON.stringify(error);
                 });
         };

         /**
          * This will build an object based on the capability data retrieved
          * from the Refstack API server. This object will contain the
          * information needed to form a report in the HTML template.
          */
         $scope.buildCapabilityObject = function () {
             var capabilities = $scope.capabilityData.capabilities;
             // This is the object template where 'count' is the number of
             // total tests that fall under the given status, and 'passedCount'
             // is the number of tests passed. The 'caps' array will contain
             // objects with details regarding each capability.
             var caps = {
                 'required': {'caps': [], 'count': 0, 'passedCount': 0},
                 'advisory': {'caps': [], 'count': 0, 'passedCount': 0},
                 'deprecated': {'caps': [], 'count': 0, 'passedCount': 0},
                 'removed': {'caps': [], 'count': 0, 'passedCount': 0}
             };
             var components = $scope.capabilityData.components;
             var cap_array = [];
             // First determine which capabilities are relevant to the target.
             if ($scope.target === 'platform') {
                 var platform_components =
                         $scope.capabilityData.platform.required;
                 // For each component required for the platform program.
                 angular.forEach(platform_components, function (component) {
                     // Get each capability belonging to each status.
                     angular.forEach(components[component],
                         function (compCapabilities) {
                             cap_array = cap_array.concat(compCapabilities);
                         });
                 });
             }
             else {
                 angular.forEach(components[$scope.target],
                     function (compCapabilities) {
                         cap_array = cap_array.concat(compCapabilities);
                     });
             }

             // Loop through each capability.
             angular.forEach(capabilities, function (value, key) {
                 // If the capability is target-relevant.
                 if (cap_array.indexOf(key) > -1) {
                     var cap = {
                         'id': key,
                         'passedTests': [],
                         'notPassedTests': []
                     };
                     caps[value.status].count += value.tests.length;
                     // Loop through each test belonging to the capability.
                     angular.forEach(value.tests, function (test_id) {
                         // If the test ID is in the results' test list, add
                         // it to the passedTests array.
                         if ($scope.resultsData.results.indexOf(test_id) > -1) {
                             cap.passedTests.push(test_id);
                         }
                         else {
                             cap.notPassedTests.push(test_id);
                         }
                     });
                     caps[value.status].passedCount += cap.passedTests.length;
                     caps[value.status].caps.push(cap);
                 }
             });
             $scope.caps = caps;
         };

         getResults();
     }
    ]);
