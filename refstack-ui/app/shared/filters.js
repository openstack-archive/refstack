var refstackApp = angular.module('refstackApp');

/** Refstack AngularJS Filters */

/**
 * Convert an object of objects to an array of objects to use with ng-repeat
 * filters.
 */
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

/**
 *  Angular filter that will capitalize the first letter of a string.
 */
refstackApp.filter('capitalize', function() {
    'use strict';

    return function (string) {
        return string.substring(0, 1).toUpperCase() + string.substring(1);
    };
});
