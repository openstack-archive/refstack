 /**
 * Refstack User Profile Controller
 * This controller handles user's profile page, where a user can view
 * account-specific information.
 */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('profileController',
    ['$scope', '$http', 'refstackApiUrl', '$state',
    function($scope, $http, refstackApiUrl, $state) {
        'use strict';
        var profile_url = refstackApiUrl + '/profile';
        $http.get(profile_url, {withCredentials: true}).
            success(function(data) {
                $scope.user = data;
            }).
            error(function() {
                $state.go('home');
            });
    }]);
