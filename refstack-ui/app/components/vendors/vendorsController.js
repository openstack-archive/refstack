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
        .controller('VendorsController', VendorsController);

    VendorsController.$inject = [
        '$rootScope', '$scope', '$http', '$state',
        'refstackApiUrl','raiseAlert'
    ];

    /**
     * RefStack Vendors Controller
     * This controller is for the '/user_vendors' or '/public_vendors' page
     * where a user can browse a listing of his/her vendors or public vendors.
     */
    function VendorsController($rootScope, $scope, $http, $state,
                               refstackApiUrl, raiseAlert) {
        var ctrl = this;

        ctrl.update = update;
        ctrl.updateData = updateData;
        ctrl._filterVendor = _filterVendor;
        ctrl.addVendor = addVendor;

        /** Check to see if this page should display user-specific vendors. */
        ctrl.isUserVendors = $state.current.name === 'userVendors';

        /** Show private vendors in list for foundation admin */
        ctrl.withPrivate = false;

        /** Properties for adding new vendor */
        ctrl.name = '';
        ctrl.description = '';

        // Should only be on user-vendors-page if authenticated.
        if (ctrl.isUserVendors && !$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.pageHeader = ctrl.isUserVendors ?
            'My Vendors' : 'Public Vendors';

        ctrl.pageParagraph = ctrl.isUserVendors ?
            'Your added vendors are listed here.' :
            'Public Vendors approved by the OpenStack Foundation are ' +
            'listed here.';

        if (ctrl.isUserVendors) {
            ctrl.authRequest = $scope.auth.doSignCheck()
                .then(ctrl.update);
        } else {
            ctrl.update();
        }

        ctrl.rawData = null;
        ctrl.isAdminView = $rootScope.auth
                           && $rootScope.auth.currentUser
                           && $rootScope.auth.currentUser.is_admin;

        /**
         * This will contact the Refstack API to get a listing of test run
         * results.
         */
        function update() {
            ctrl.showError = false;
            ctrl.data = null;
            // Construct the API URL based on user-specified filters.
            var contentUrl = refstackApiUrl + '/vendors';
            if (typeof ctrl.rawData == 'undefined'
                    || ctrl.rawData === null) {
                ctrl.vendorsRequest =
                    $http.get(contentUrl).success(function (data) {
                        ctrl.rawData = data;
                        ctrl.updateData();
                    }).error(function (error) {
                        ctrl.rawData = null;
                        ctrl.showError = true;
                        ctrl.error =
                            'Error retrieving vendors listing from server: ' +
                            angular.toJson(error);
                    });
            } else {
                ctrl.updateData();
            }
        }

        /**
         * This will update data for view with current settings on page.
         */
        function updateData() {
            ctrl.data = {};
            ctrl.data.vendors = ctrl.rawData.vendors.filter(function(vendor) {
                return ctrl._filterVendor(vendor);
            });
            ctrl.data.vendors.sort(function(a, b) {
                if (a.type > b.type) {
                    return 1;
                }
                if (a.type < b.type) {
                    return -1;
                }
                return a.name.localeCompare(b.name);
            });
        }

        /**
         * Returns true if vendor can be displayed on this page.
         */
        function _filterVendor(vendor) {
            if (!ctrl.isUserVendors) {
                return (vendor.type == 0 || vendor.type == 3);
            }

            if (!$rootScope.auth || !$rootScope.auth.currentUser) {
                return false;
            }

            if ($rootScope.auth.currentUser.is_admin) {
                return vendor.type != 1 || ctrl.withPrivate;
            }

            return vendor.can_manage;
        }

        /**
         * This will add a new vendor record.
         */
        function addVendor() {
            var url = refstackApiUrl + '/vendors';
            var data = {
                name: ctrl.name,
                description: ctrl.description
            };
            ctrl.name = '';
            ctrl.description = '';
            $http.post(url, data).success(function (data) {
                ctrl.rawData = null;
                ctrl.update();
            }).error(function (error) {
                ctrl.showError = true;
                ctrl.error =
                    'Error adding new vendor: ' + angular.toJson(error);
            });
        }
    }
})();
