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
        .controller('VendorController', VendorController);

    VendorController.$inject = [
        '$rootScope', '$scope', '$http', '$state', '$stateParams', '$window',
        'refstackApiUrl', 'raiseAlert', 'confirmModal'
    ];

    /**
     * RefStack Vendor Controller
     * This controller is for the '/vendor/' details page where owner can
     * view details of the Vendor and manage users.
     */
    function VendorController($rootScope, $scope, $http, $state, $stateParams,
            $window, refstackApiUrl, raiseAlert, confirmModal) {
        var ctrl = this;

        ctrl.getVendor = getVendor;
        ctrl.getVendorUsers = getVendorUsers;
        ctrl.registerVendor = registerVendor;
        ctrl.approveVendor = approveVendor;
        ctrl.declineVendor = declineVendor;
        ctrl.deleteVendor = deleteVendor;
        ctrl.removeUserFromVendor = removeUserFromVendor;
        ctrl.addUserToVendor = addUserToVendor;

        /** The vendor id extracted from the URL route. */
        ctrl.vendorId = $stateParams.vendorID;

        // Should only be on user-vendors-page if authenticated.
        if (!$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        /**
         * This will contact the Refstack API to get a vendor information.
         */
        function getVendor() {
            ctrl.showError = false;
            ctrl.vendor = null;
            // Construct the API URL based on user-specified filters.
            var contentUrl = refstackApiUrl + '/vendors/' + ctrl.vendorId;
            ctrl.vendorRequest =
                $http.get(contentUrl).success(function(data) {
                    ctrl.vendor = data;
                    var isAdmin = $rootScope.auth.currentUser.is_admin;
                    ctrl.vendor.canDelete = ctrl.vendor.type != 0
                        && (ctrl.vendor.can_manage || isAdmin);
                    ctrl.vendor.canRegister =
                        ctrl.vendor.type == 1;
                    ctrl.vendor.canApprove = isAdmin;
                    ctrl.vendorProperties = angular.fromJson(data.properties);
                }).error(function(error) {
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving from server: ' +
                        angular.toJson(error);
                });
        }
        ctrl.getVendor();

        /**
         * This will 'send' application for registration.
         */
        function registerVendor() {
            var url = [refstackApiUrl, '/vendors/', ctrl.vendorId,
                       '/action'].join('');
            $http.post(url, {register: null}).success(function() {
                ctrl.getVendor();
            }).error(function(error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * This will approve application for registration.
         */
        function approveVendor() {
            var url = [refstackApiUrl, '/vendors/', ctrl.vendorId,
                       '/action'].join('');
            $http.post(url, {approve: null}).success(function() {
                ctrl.getVendor();
            }).error(function(error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * This will decline a vendor's application for registration.
         */
        function declineVendor() {
            confirmModal('Please input decline reason', function(reason) {
                var url = [refstackApiUrl, '/vendors/', ctrl.vendorId,
                           '/action'].join('');
                $http.post(url, {deny: null, reason: reason}).success(
                    function() {
                        ctrl.getVendor();
                    }).error(function(error) {
                        raiseAlert('danger', 'Error: ', error.detail);
                    });
            });
        }

        /**
         * Delete the current vendor.
         */
        function deleteVendor() {
            var url = [refstackApiUrl, '/vendors/', ctrl.vendorId].join('');
            $http.delete(url).success(function () {
                $window.location.href = '/';
            }).error(function (error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * Updates list of users in the vendor's group
         */
        function getVendorUsers() {
            ctrl.showError = false;
            var contentUrl = refstackApiUrl + '/vendors/' + ctrl.vendorId
                              + '/users';
            ctrl.usersRequest =
                $http.get(contentUrl).success(function(data) {
                    ctrl.vendorUsers = data;
                    ctrl.currentUser = $rootScope.auth.currentUser.openid;
                }).error(function(error) {
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving from server: ' +
                        angular.toJson(error);
                });
        }
        ctrl.getVendorUsers();

        /**
         * Removes user with specific openid from vendor's group
         * @param {Object} openid
         */
        function removeUserFromVendor(openid) {
            var url = [refstackApiUrl, '/vendors/', ctrl.vendorId,
                       '/users/', btoa(openid)].join('');
            $http.delete(url).success(function () {
                ctrl.getVendorUsers();
            }).error(function (error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * Adds a user to a vendor group given an Open ID.
         * @param {Object} openid
         */
        function addUserToVendor(openid) {
            var url = [refstackApiUrl, '/vendors/', ctrl.vendorId,
                       '/users/', btoa(openid)].join('');
            $http.put(url).success(function() {
                ctrl.userToAdd = '';
                ctrl.getVendorUsers();
            }).error(function(error) {
                raiseAlert('danger', 'Problem adding user. ' +
                                     'Is the Open ID correct? Error: ',
                           error.detail);
            });
        }
    }
})();
