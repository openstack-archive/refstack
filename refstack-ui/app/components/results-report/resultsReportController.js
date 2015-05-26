/* Refstack Results Report Controller */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('resultsReportController',
    ['$scope', '$http', '$stateParams', 'refstackApiUrl',
     function ($scope, $http, $stateParams, refstackApiUrl) {
         'use strict';

         $scope.testId = $stateParams.testID;
         $scope.hideTests = true;
         $scope.target = 'platform';
         $scope.requiredOpen = true;

         $scope.targetMappings = {
             'platform': 'Openstack Powered Platform',
             'compute': 'OpenStack Powered Compute',
             'object': 'OpenStack Powered Object Storage'
         };

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

         $scope.buildCapabilityObject = function () {
             var capabilities = $scope.capabilityData.capabilities;
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

             angular.forEach(capabilities, function (value, key) {
                 if (cap_array.indexOf(key) > -1) {
                     var cap = {
                         'id': key,
                         'passedTests': [],
                         'notPassedTests': []
                     };
                     caps[value.status].count += value.tests.length;
                     angular.forEach(value.tests, function (test_id) {
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
