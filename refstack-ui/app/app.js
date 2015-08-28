/** Main app module where application dependencies are listed. */
var refstackApp = angular.module('refstackApp', [
    'ui.router', 'ui.bootstrap', 'cgBusy', 'ngResource']);

/**
 * Handle application routing. Specific templates and controllers will be
 * used based on the URL route.
 */
refstackApp.config([
    '$stateProvider', '$urlRouterProvider',
    function ($stateProvider, $urlRouterProvider) {
        'use strict';

        $urlRouterProvider.otherwise('/');
        $stateProvider.
            state('home', {
                url: '/',
                templateUrl: '/components/home/home.html'
            }).
            state('about', {
                url: '/about',
                templateUrl: '/components/about/about.html'
            }).
            state('capabilities', {
                url: '/capabilities',
                templateUrl: '/components/capabilities/capabilities.html',
                controller: 'capabilitiesController'
            }).
            state('community_results', {
                url: '/community_results',
                templateUrl: '/components/results/results.html',
                controller: 'resultsController'
            }).
            state('user_results', {
                url: '/user_results',
                templateUrl: '/components/results/results.html',
                controller: 'resultsController'
            }).
            state('resultsDetail', {
                url: '/results/:testID',
                templateUrl: '/components/results-report/resultsReport.html',
                controller: 'resultsReportController'
            }).
            state('profile', {
                url: '/profile',
                templateUrl: '/components/profile/profile.html',
                controller: 'profileController'
            });
    }
]);

/**
 * Injections in $rootscope
 */

refstackApp.run(['$http', '$rootScope', '$window', '$state', 'refstackApiUrl',
    function($http, $rootScope, $window, $state, refstackApiUrl) {
        'use strict';

        /**
         * This function injects sign in function in all scopes
         */

        $rootScope.auth = {};

        var sign_in_url = refstackApiUrl + '/auth/signin';
        $rootScope.auth.doSignIn = function () {
            $window.location.href = sign_in_url;
        };

        /**
         * This function injects sign out function in all scopes
         */
        var sign_out_url = refstackApiUrl + '/auth/signout';
        $rootScope.auth.doSignOut = function () {
            $rootScope.currentUser = null;
            $rootScope.isAuthenticated = false;
            $window.location.href = sign_out_url;
        };

        /**
         * This block tries to authenticate user
         */
        var profile_url = refstackApiUrl + '/profile';
        $rootScope.auth.doSignCheck = function () {
            return $http.get(profile_url, {withCredentials: true}).
                success(function (data) {
                    $rootScope.auth.currentUser = data;
                    $rootScope.auth.isAuthenticated = true;
                }).
                error(function () {
                    $rootScope.auth.currentUser = null;
                    $rootScope.auth.isAuthenticated = false;
                    $state.go('home');
                });
        };
        $rootScope.auth.doSignCheck();
    }
]);

/**
 * Load config and start up the angular application.
 */
angular.element(document).ready(function () {
    'use strict';

    var $http = angular.injector(['ng']).get('$http');

    function startApp(config) {
        // Add config options as constants.
        for (var key in config) {
            angular.module('refstackApp').constant(key, config[key]);
        }
        angular.bootstrap(document, ['refstackApp']);
    }

    $http.get('config.json').success(function (data) {
        startApp(data);
    }).error(function () {
        startApp({});
    });
});
