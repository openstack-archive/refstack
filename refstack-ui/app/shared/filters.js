/* Refstack Filters */

var refstackApp = angular.module('refstackApp');

// Convert an object of objects to an array of objects to use with ng-repeat
// filters.
refstackApp.filter('arrayConverter', function () {
    'use strict';

    return function (objects) {
        var array = [];
        angular.forEach(objects, function (object, key) {
            object.id = key;
            array.push(object);
        });
        return array;
    };
});
