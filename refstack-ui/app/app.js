'use strict';

/* App Module */

var refstackApp = angular.module('refstackApp', [
  'ui.router', 'ui.bootstrap']);

refstackApp.config(['$stateProvider', '$urlRouterProvider',
    function($stateProvider, $urlRouterProvider) {
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
                templateUrl: '/components/results/results.html'
            })
    }]);

