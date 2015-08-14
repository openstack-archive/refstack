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

         /** The various possible capability statuses. */
         $scope.status = {
             required: true,
             advisory: false,
             deprecated: false,
             removed: false
         };

         /**
          * The template to load for displaying capability details. The value
          * of this depends on the schema version of the capabilities file.
          */
         $scope.detailsTemplate = null;

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
                     $scope.detailsTemplate = 'components/capabilities/' +
                                              'partials/capabilityDetailsV' +
                                              data.schema + '.html';
                     $scope.updateTargetCapabilities();
                 }).error(function (error) {
                     $scope.showError = true;
                     $scope.capabilities = null;
                     $scope.error = 'Error retrieving capabilities: ' +
                         JSON.stringify(error);
                 });
         };

         /**
          * This will update the scope's 'targetCapabilities' object with
          * capabilities belonging to the selected OpenStack marketing program
          * (programs typically correspond to 'components' in the DefCore
          * schema). Each capability will have its status mapped to it.
          */
         $scope.updateTargetCapabilities = function () {
             $scope.targetCapabilities = {};
             var components = $scope.capabilities.components;
             var targetCaps = $scope.targetCapabilities;

             // The 'platform' target is comprised of multiple components, so
             // we need to get the capabilities belonging to each of its
             // components.
             if ($scope.target === 'platform') {
                 var platform_components =
                     $scope.capabilities.platform.required;

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
         };

         $scope.getVersionList();

         /**
          * This filter will check if a capability's status corresponds
          * to a status that is checked/selected in the UI. This filter
          * is meant to be used with the ng-repeat directive.
          * @param {Object} capability
          * @returns {Boolean} True if capability's status is selected
          */
         $scope.filterStatus = function (capability) {
             var caps = $scope.targetCapabilities;
             return ($scope.status.required &&
                     caps[capability.id] === 'required') ||
                    ($scope.status.advisory &&
                     caps[capability.id] === 'advisory') ||
                    ($scope.status.deprecated &&
                     caps[capability.id] === 'deprecated') ||
                    ($scope.status.removed &&
                     caps[capability.id] === 'removed');
         };

         /**
          * This function will get the length of an Object/dict based on
          * the number of keys it has.
          * @param {Object} object
          * @returns {Number} length of object
          */
         $scope.getObjectLength = function (object) {
             return Object.keys(object).length;
         };
     }]);
