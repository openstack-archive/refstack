/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    /** Main app module where application dependencies are listed. */
    angular
        .module('refstackApp', [
            'ui.router','ui.bootstrap', 'cgBusy',
            'ngResource', 'angular-confirm'
        ]);

    angular
        .module('refstackApp')
        .config(configureRoutes);

    configureRoutes.$inject = ['$stateProvider', '$urlRouterProvider'];

    /**
     * Handle application routing. Specific templates and controllers will be
     * used based on the URL route.
     */
    function configureRoutes($stateProvider, $urlRouterProvider) {
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
                controller: 'CapabilitiesController as ctrl'
            }).
            state('communityResults', {
                url: '/community_results',
                templateUrl: '/components/results/results.html',
                controller: 'ResultsController as ctrl'
            }).
            state('userResults', {
                url: '/user_results',
                templateUrl: '/components/results/results.html',
                controller: 'ResultsController as ctrl'
            }).
            state('resultsDetail', {
                url: '/results/:testID',
                templateUrl: '/components/results-report' +
                             '/resultsReport.html',
                controller: 'ResultsReportController as ctrl'
            }).
            state('profile', {
                url: '/profile',
                templateUrl: '/components/profile/profile.html',
                controller: 'ProfileController as ctrl'
            }).
            state('authFailure', {
                url: '/auth_failure/:message',
                templateUrl: '/components/home/home.html',
                controller: 'AuthFailureController as ctrl'
            });
    }

    angular
        .module('refstackApp')
        .run(setup);

    setup.$inject = [
        '$http', '$rootScope', '$window', '$state', 'refstackApiUrl'
    ];

    /**
     * Set up the app with injections into $rootscope. This is mainly for auth
     * functions.
     */
    function setup($http, $rootScope, $window, $state, refstackApiUrl) {

        /**
         * This function injects sign in function in all scopes
         */

        $rootScope.auth = {};
        $rootScope.auth.doSignIn = doSignIn;
        $rootScope.auth.doSignOut = doSignOut;
        $rootScope.auth.doSignCheck = doSignCheck;

        var sign_in_url = refstackApiUrl + '/auth/signin';
        var sign_out_url = refstackApiUrl + '/auth/signout';
        var profile_url = refstackApiUrl + '/profile';

        /** This function initiates a sign in. */
        function doSignIn() {
            $window.location.href = sign_in_url;
        }

        /** This function will initate a sign out. */
        function doSignOut() {
            $rootScope.currentUser = null;
            $rootScope.isAuthenticated = false;
            $window.location.href = sign_out_url;
        }

        /**
         * This function checks to see if a user is logged in and
         * authenticated.
         */
        function doSignCheck() {
            return $http.get(profile_url, {withCredentials: true}).
                success(function (data) {
                    $rootScope.auth.currentUser = data;
                    $rootScope.auth.isAuthenticated = true;
                }).
                error(function () {
                    $rootScope.auth.currentUser = null;
                    $rootScope.auth.isAuthenticated = false;
                });
        }

        $rootScope.auth.doSignCheck();
    }

    angular
        .element(document)
        .ready(loadConfig);

    /**
     * Load config and start up the angular application.
     */
    function loadConfig() {

        var $http = angular.injector(['ng']).get('$http');

        /**
         * Store config variables as constants, and start the app.
         */
        function startApp(config) {
            // Add config options as constants.
            angular.forEach(config, function(value, key) {
                angular.module('refstackApp').constant(key, value);
            });

            angular.bootstrap(document, ['refstackApp']);
        }

        $http.get('config.json').success(function (data) {
            startApp(data);
        }).error(function () {
            startApp({});
        });
    }
})();
