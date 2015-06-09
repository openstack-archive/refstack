var refstackApp = angular.module('refstackApp');

/**
 * Refstack Header Controller
 * This controller is for the header template which contains the site
 * navigation.
 */
refstackApp.controller('headerController',
    ['$scope', '$location', function ($scope, $location) {
        'use strict';

        /** Whether the Navbar is collapsed for small displays. */
        $scope.navbarCollapsed = true;

        /**
         * This determines whether a button should be in the active state based
         * on the URL.
         */
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
