/* Refstack Header Controller */

var refstackApp = angular.module('refstackApp');
refstackApp.controller('headerController',
    ['$scope', '$location', function ($scope, $location) {
        'use strict';

        $scope.navbarCollapsed = true;
        $scope.isActive = function (viewLocation) {
            var path = $location.path().substr(0, viewLocation.length);
            if (path === viewLocation) {
                // Make sure "/" only matches when viewLocation is "/".
                if (!($location.path().substr(0).length > 1 &&
                    viewLocation.length === 1 )) {
                    return true;
                }
            }
            return false;
        };
    }]);
