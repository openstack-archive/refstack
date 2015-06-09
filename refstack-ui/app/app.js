/** Main app module where application dependencies are listed. */
var refstackApp = angular.module('refstackApp', [
    'ui.router', 'ui.bootstrap', 'cgBusy']);

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
            state('results', {
                url: '/results',
                templateUrl: '/components/results/results.html',
                controller: 'resultsController'
            }).
            state('resultsDetail', {
                url: '/results/:testID',
                templateUrl: '/components/results-report/resultsReport.html',
                controller: 'resultsReportController'
            });
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
