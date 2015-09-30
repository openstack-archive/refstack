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

    /**
     * Convert an object of objects to an array of objects to use with ng-repeat
     * filters.
     */
    angular
        .module('refstackApp')
        .filter('arrayConverter', arrayConverter);

    /**
     * Convert an object of objects to an array of objects to use with ng-repeat
     * filters.
     */
    function arrayConverter() {
        return function (objects) {
            var array = [];
            angular.forEach(objects, function (object, key) {
                object.id = key;
                array.push(object);
            });
            return array;
        };
    }

    angular
        .module('refstackApp')
        .filter('capitalize', capitalize);

    /**
     * Angular filter that will capitalize the first letter of a string.
     */
    function capitalize() {
        return function (string) {
            return string.substring(0, 1).toUpperCase() + string.substring(1);
        };
    }
})();
