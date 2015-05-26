/* Refstack Capabilities Controller */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('capabilitiesController',
    ['$scope', '$http', 'refstackApiUrl',
     function ($scope, $http, refstackApiUrl) {
         'use strict';

         $scope.hideAchievements = true;
         $scope.hideTests = true;
         $scope.target = 'platform';
         $scope.status = {
             required: 'required',
             advisory: '',
             deprecated: '',
             removed: ''
         };

         $scope.getVersionList = function () {
             var content_url = refstackApiUrl + '/capabilities';
             $scope.versionsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.versionList = data.sort().reverse();
                     $scope.version = $scope.versionList[0];
                     $scope.update();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.error = 'Error retrieving version list: ' +
                         JSON.stringify(error);
                 });
         };

         $scope.update = function () {
             var content_url = refstackApiUrl + '/capabilities/' +
                 $scope.version;
             $scope.capsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.capabilities = data;
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.capabilities = null;
                     $scope.error = 'Error retrieving capabilities: ' +
                         JSON.stringify(error);
                 });
         };

         $scope.getVersionList();

         $scope.filterProgram = function (capability) {
             var components = $scope.capabilities.components;
             var cap_array = [];

             if ($scope.target === 'platform') {
                 var platform_components =
                         $scope.capabilities.platform.required;
                 // For each component required for the platform program.
                 angular.forEach(platform_components, function (component) {
                     // Get each capability belonging to each status.
                     angular.forEach(components[component],
                         function (capabilities) {
                             cap_array = cap_array.concat(capabilities);
                         });
                 });
             }
             else {
                 angular.forEach(components[$scope.target],
                     function (capabilities) {
                         cap_array = cap_array.concat(capabilities);
                     });
             }
             return (cap_array.indexOf(capability.id) > -1);
         };

         $scope.filterStatus = function (capability) {
             return capability.status === $scope.status.required ||
                 capability.status === $scope.status.advisory ||
                 capability.status === $scope.status.deprecated ||
                 capability.status === $scope.status.removed;
         };
     }]);
