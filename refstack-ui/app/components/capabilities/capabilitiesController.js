'use strict';

/* Refstack Capabilities Controller */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('capabilitiesController', ['$scope', '$http', function($scope, $http) {
    $scope.version = '2015.03';
    $scope.hideAchievements = true;
    $scope.hideTests = true;
    $scope.target = 'platform';
    $scope.status = {
        required: 'required',
        advisory: '',
        deprecated: '',
        removed: ''
    };

    $scope.update = function() {
        // Rate-limiting is an issue with this URL. Using a local copy for now.
        // var content_url = 'https://api.github.com/repos/openstack/defcore/contents/'.concat($scope.version, '.json');
        var content_url = 'assets/capabilities/'.concat($scope.version, '.json');
        $http.get(content_url).success(function(data) {
            //$scope.data = data;
            //$scope.capabilities = JSON.parse(atob($scope.data.content.replace(/\s/g, '')));
            $scope.capabilities = data;
        }).error(function(error) {
            console.log(error);
            $scope.capabilities = 'Error retrieving capabilities.';
        });
    }
    $scope.update()

    $scope.filterProgram = function(capability){
        var components = $scope.capabilities.components;
        if ($scope.target === 'platform') {
            var platform_components = $scope.capabilities.platform.required;
            var cap_array = [];
            // For each component required for the platform program.
            angular.forEach(platform_components, function(component) {
                // Get each capability belonging to each status.
                angular.forEach(components[component], function(capabilities) {
                    cap_array = cap_array.concat(capabilities);
                });
            });
            return (cap_array.indexOf(capability.id) > -1);
        }
        else {
            var cap_array = [];
            angular.forEach(components[$scope.target], function(capabilities) {
                cap_array = cap_array.concat(capabilities);
            });
            return (cap_array.indexOf(capability.id) > -1);
        }
    };

    $scope.filterStatus = function(capability){
        return capability.status === $scope.status.required ||
            capability.status === $scope.status.advisory ||
            capability.status === $scope.status.deprecated ||
            capability.status === $scope.status.removed;
    };
}]);
