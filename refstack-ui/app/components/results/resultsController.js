'use strict';

/* Refstack Results Controller */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('resultsController', ['$scope', '$http', '$filter', 'refstackApiUrl', function($scope, $http, $filter, refstackApiUrl) {
    $scope.currentPage = 1;
    $scope.itemsPerPage = 20;
    $scope.maxSize = 5;
    $scope.startDate = "";
    $scope.endDate = "";
    $scope.update = function() {
        $scope.showError = false;
        var content_url = refstackApiUrl + '/results?page=' + $scope.currentPage;
        var start = $filter('date')($scope.startDate, "yyyy-MM-dd");
        if (start) {
            content_url = content_url + "&start_date=" + start + " 00:00:00";
        }
        var end = $filter('date')($scope.endDate, "yyyy-MM-dd");
        if (end) {
            content_url = content_url + "&end_date=" + end + " 23:59:59";
        }

        $scope.resultsRequest = $http.get(content_url).success(function(data) {
            $scope.data = data;
            $scope.totalItems = $scope.data.pagination.total_pages * $scope.itemsPerPage;
            $scope.currentPage = $scope.data.pagination.current_page;
        }).error(function(error) {
            $scope.data = null;
            $scope.totalItems = 0
            $scope.showError = true
            $scope.error = "Error retrieving results listing from server: " + JSON.stringify(error);
        });
    }

    $scope.update();

    // This is called when a date filter calendar is opened.
    $scope.open = function($event, openVar) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope[openVar] = true;
    };

    $scope.clearFilters = function() {
        $scope.startDate = null;
        $scope.endDate = null;
        $scope.update();
    };
}]);
