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

    angular
        .module('refstackApp')
        .controller('HeaderController', HeaderController);

    HeaderController.$inject = ['$location'];

    /**
     * Refstack Header Controller
     * This controller is for the header template which contains the site
     * navigation.
     */
    function HeaderController($location) {
        var ctrl = this;

        ctrl.isActive = isActive;
        ctrl.isCatalogActive = isCatalogActive;

        /** Whether the Navbar is collapsed for small displays. */
        ctrl.navbarCollapsed = true;

        /**
         * This determines whether a button should be in the active state based
         * on the URL.
         */
        function isActive(viewLocation) {
            var path = $location.path().substr(0, viewLocation.length);
            if (path === viewLocation) {
                // Make sure "/" only matches when viewLocation is "/".
                if (!($location.path().substr(0).length > 1 &&
                    viewLocation.length === 1 )) {
                    return true;
                }
            }
            return false;
        }

        /** This determines the active state for the catalog dropdown. Type
         * parameter should be passed in to specify if the catalog is the
         * public or user one.
         */
        function isCatalogActive(type) {
            return ctrl.isActive('/' + type + '_vendors');
        }
    }
})();
