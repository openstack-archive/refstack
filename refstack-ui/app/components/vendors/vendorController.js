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
        '$uibModal', 'refstackApiUrl', 'raiseAlert', 'confirmModal'
    ];

    /**
     * RefStack Vendor Controller
     * This controller is for the '/vendor/' details page where owner can
     * view details of the Vendor and manage users.
     */
    function VendorController($rootScope, $scope, $http, $state, $stateParams,
            $window, $uibModal, refstackApiUrl, raiseAlert, confirmModal) {
        var ctrl = this;

        ctrl.getVendor = getVendor;
        ctrl.getVendorUsers = getVendorUsers;
        ctrl.getVendorProducts = getVendorProducts;
        ctrl.getProductTypeDescription = getProductTypeDescription;
        ctrl.registerVendor = registerVendor;
        ctrl.approveVendor = approveVendor;
        ctrl.declineVendor = declineVendor;
        ctrl.deleteVendor = deleteVendor;
        ctrl.removeUserFromVendor = removeUserFromVendor;
        ctrl.addUserToVendor = addUserToVendor;
        ctrl.openVendorEditModal = openVendorEditModal;

        /** The vendor id extracted from the URL route. */
        ctrl.vendorId = $stateParams.vendorID;

        // Should only be on user-vendors-page if authenticated.
        if (!$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.getVendor();
        ctrl.getVendorUsers();
        ctrl.getVendorProducts();

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
                    ctrl.vendor.canDelete = ctrl.vendor.canEdit =
                        ctrl.vendor.type != 0
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
                var content = {deny: null, registration_decline_reason: reason};
                $http.post(url, content).success(
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

        /**
         * Updates list of users in the vendor's group
         */
        function getVendorProducts() {
            ctrl.showError = false;
            var contentUrl = refstackApiUrl + '/products?organization_id='
                              + ctrl.vendorId;
            ctrl.productsRequest =
                $http.get(contentUrl).success(function(data) {
                    ctrl.vendorProducts = data.products;
                }).error(function(error) {
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving from server: ' +
                        angular.toJson(error);
                });
        }

        /**
         * Get the product type description given the type integer.
         */
        function getProductTypeDescription(product_type) {
            switch (product_type) {
                case 0:
                    return 'Distro';
                case 1:
                    return 'Public Cloud';
                case 2:
                    return 'Hosted Private Cloud';
                default:
                    return 'Unknown';
            }
        }

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

        /**
         * This will open the modal that will allow a user to edit
         */
        function openVendorEditModal() {
            $uibModal.open({
                templateUrl: '/components/vendors/partials' +
                        '/vendorEditModal.html',
                backdrop: true,
                windowClass: 'modal',
                animation: true,
                controller: 'VendorEditModalController as modal',
                size: 'lg',
                resolve: {
                    vendor: function () {
                        return ctrl.vendor;
                    }
                }
            });
        }
    }

    angular
        .module('refstackApp')
        .controller('VendorEditModalController', VendorEditModalController);

    VendorEditModalController.$inject = [
        '$rootScope',
        '$uibModalInstance', '$http', '$state', 'vendor', 'refstackApiUrl'
    ];

    /**
     * Vendor Edit Modal Controller
     * This controls the modal that allows editing a vendor.
     */
    function VendorEditModalController($rootScope, $uibModalInstance, $http,
        $state, vendor, refstackApiUrl) {

        var ctrl = this;

        ctrl.close = close;
        ctrl.addField = addField;
        ctrl.saveChanges = saveChanges;
        ctrl.removeProperty = removeProperty;

        ctrl.vendor = angular.copy(vendor);
        ctrl.vendorName = vendor.name;
        ctrl.vendorProperties = [];
        ctrl.isAdmin = $rootScope.auth.currentUser.is_admin;

        parseVendorProperties();

        /**
         * Close the vendor edit modal.
         */
        function close() {
            $uibModalInstance.dismiss('exit');
        }

        /**
         * Push a blank property key-value pair into the vendorProperties
         * array. This will spawn new input boxes.
         */
        function addField() {
            ctrl.vendorProperties.push({'key': '', 'value': ''});
        }

        /**
         * Send a PUT request to the server with the changes.
         */
        function saveChanges() {
            ctrl.showError = false;
            ctrl.showSuccess = false;
            var url = [refstackApiUrl, '/vendors/', ctrl.vendor.id].join('');
            var properties = propertiesToJson();
            var content = {'description': ctrl.vendor.description,
                           'properties': properties};
            if (ctrl.vendorName != ctrl.vendor.name) {
                content.name = ctrl.vendor.name;
            }
            $http.put(url, content).success(function() {
                ctrl.showSuccess = true;
                $state.reload();
            }).error(function(error) {
                ctrl.showError = true;
                ctrl.error = error.detail;
            });
        }

        /**
         * Remove a property from the vendorProperties array at the given index.
         */
        function removeProperty(index) {
            ctrl.vendorProperties.splice(index, 1);
        }

        /**
         * Parse the vendor properties and put them in a format more suitable
         * for forms.
         */
        function parseVendorProperties() {
            var props = angular.fromJson(ctrl.vendor.properties);
            angular.forEach(props, function(value, key) {
                ctrl.vendorProperties.push({'key': key, 'value': value});
            });
        }

        /**
         * Convert the list of property objects to a dict containing the
         * each key-value pair..
         */
        function propertiesToJson() {
            var properties = {};
            for (var i = 0, len = ctrl.vendorProperties.length; i < len; i++) {
                var prop = ctrl.vendorProperties[i];
                if (prop.key && prop.value) {
                    properties[prop.key] = prop.value;
                }
            }
            return properties;
        }
    }
})();
