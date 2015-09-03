var refstackApp = angular.module('refstackApp');

/**
 * Refstack Results Controller
 * This controller is for the '/results' page where a user can browse
 * a listing of community uploaded results.
 */
refstackApp.controller('resultsController',
    ['$scope', '$http', '$filter', '$state', 'refstackApiUrl',
     function ($scope, $http, $filter, $state, refstackApiUrl) {
         'use strict';

         /** Initial page to be on. */
         $scope.currentPage = 1;

         /**
          * How many results should display on each page. Since pagination
          * is server-side implemented, this value should match the
          * 'results_per_page' configuration of the Refstack server which
          * defaults to 20.
          */
         $scope.itemsPerPage = 20;

         /**
          * How many page buttons should be displayed at max before adding
          * the '...' button.
          */
         $scope.maxSize = 5;

         /** The upload date lower limit to be used in filtering results. */
         $scope.startDate = '';

         /** The upload date upper limit to be used in filtering results. */
         $scope.endDate = '';

         $scope.isUserResults = $state.current.name === 'userResults';
         $scope.pageHeader = $scope.isUserResults ?
             'Private test results' : 'Community test results';
         /**
          * This will contact the Refstack API to get a listing of test run
          * results.
          */
         $scope.update = function () {
             $scope.showError = false;
             // Construct the API URL based on user-specified filters.
             var content_url = refstackApiUrl + '/results?page=' +
                 $scope.currentPage;
             var start = $filter('date')($scope.startDate, 'yyyy-MM-dd');
             if (start) {
                 content_url =
                     content_url + '&start_date=' + start + ' 00:00:00';
             }
             var end = $filter('date')($scope.endDate, 'yyyy-MM-dd');
             if (end) {
                 content_url = content_url + '&end_date=' + end + ' 23:59:59';
             }
             if ($scope.isUserResults) {
                 content_url = content_url + '&signed';
             }
             $scope.resultsRequest =
                 $http.get(content_url).success(function (data) {
                     $scope.data = data;
                     $scope.totalItems = $scope.data.pagination.total_pages *
                         $scope.itemsPerPage;
                     $scope.currentPage = $scope.data.pagination.current_page;
                 }).error(function (error) {
                     $scope.data = null;
                     $scope.totalItems = 0;
                     $scope.showError = true;
                     $scope.error =
                         'Error retrieving results listing from server: ' +
                         JSON.stringify(error);
                 });
         };
         if ($scope.isUserResults) {
             $scope.authRequest = $scope.auth.doSignCheck()
                 .then($scope.update);
         } else {
             $scope.update();
         }

         /**
          * This is called when the date filter calendar is opened. It
          * does some event handling, and sets a scope variable so the UI
          * knows which calendar was opened.
          * @param {Object} $event - The Event object
          * @param {String} openVar - Tells which calendar was opened
          */
         $scope.open = function ($event, openVar) {
             $event.preventDefault();
             $event.stopPropagation();
             $scope[openVar] = true;
         };

         /**
          * This function will clear all filters and update the results
          * listing.
          */
         $scope.clearFilters = function () {
             $scope.startDate = null;
             $scope.endDate = null;
             $scope.update();
         };
     }]);
