var refstackApp = angular.module('refstackApp');

/**
 * Refstack Capabilities Controller
 * This controller is for the '/capabilities' page where a user can browse
 * through tests belonging to DefCore-defined capabilities.
 */
refstackApp.controller('capabilitiesController',
    ['$scope', '$http', 'refstackApiUrl',
     function ($scope, $http, refstackApiUrl) {
         'use strict';

         /** Whether to hide/collapse the achievements for each capability. */
         $scope.hideAchievements = true;

         /** Whether to hide/collapse the tests for each capability. */
         $scope.hideTests = true;

         /** The target OpenStack marketing program to show capabilities for. */
         $scope.target = 'platform';

         /**
          * The various possible capability statuses. The true value for each
          * status is the name of the key, so by default only required
          * capabilities will be shown.
          */
         $scope.status = {
             required: 'required',
             advisory: '',
             deprecated: '',
             removed: ''
         };

         /**
          * Retrieve an array of available capability files from the Refstack
          * API server, sort this array reverse-alphabetically, and store it in
          * a scoped variable. The scope's selected version is initialized to
          * the latest (i.e. first) version here as well. After a successful API
          * call, the function to update the capabilities is called.
          * Sample API return array: ["2015.03.json", "2015.04.json"]
          */
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

         /**
          * This will contact the Refstack API server to retrieve the JSON
          * content of the capability file corresponding to the selected
          * version.
          */
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

         /**
          * This is a filter that will check if a specific capability belongs
          * to the selected OpenStack marketing program (programs typically
          * correspond to 'components' in the DefCore schema). This filter
          * is meant to be used with the ng-repeat directive.
          * @param {Object} A capability object from the capabilities JSON
          * @returns {Boolean} True if capability belongs to program
          */
         $scope.filterProgram = function (capability) {
             var components = $scope.capabilities.components;
             var cap_array = [];

             // The 'platform' target is comprised of multiple components, so
             // we need to get the capabilities belonging to each of its
             // components.
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

         /**
          * This filter will check if a capability's status corresponds
          * to a status that is checked/selected in the UI. This filter
          * is meant to be used with the ng-repeat directive.
          * @param {Object} capability
          * @returns {Boolean} True if capability's status is selected
          */
         $scope.filterStatus = function (capability) {
             return capability.status === $scope.status.required ||
                 capability.status === $scope.status.advisory ||
                 capability.status === $scope.status.deprecated ||
                 capability.status === $scope.status.removed;
         };
     }]);
