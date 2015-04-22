var refstackApp = angular.module('refstackApp');

 /**
 * Refstack Auth Controller
 * This controller handles account authentication for users.
 */

refstackApp.controller('authController',
    ['$scope', '$window', '$rootScope', 'refstackApiUrl',
    function($scope, $window, $rootScope, refstackApiUrl){
        'use strict';
        var sign_in_url = refstackApiUrl + '/auth/signin';
        $scope.doSignIn = function () {
            $window.location.href = sign_in_url;
        };

        var sign_out_url = refstackApiUrl + '/auth/signout';
        $scope.doSignOut = function () {
            $rootScope.currentUser = null;
            $window.location.href = sign_out_url;
        };

        $scope.isAuthenticated = function () {
            if ($scope.currentUser) {
                return !!$scope.currentUser.openid;
            }
            return false;
        };
    }]);
