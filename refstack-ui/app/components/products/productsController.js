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
        .controller('ProductsController', ProductsController);

    ProductsController.$inject = [
        '$rootScope', '$scope', '$http', '$state',
        'refstackApiUrl','raiseAlert'
    ];

    /**
     * RefStack Products Controller
     */
    function ProductsController($rootScope, $scope, $http, $state,
                                refstackApiUrl, raiseAlert) {
        var ctrl = this;

        ctrl.update = update;
        ctrl.updateData = updateData;
        ctrl._filterProduct = _filterProduct;
        ctrl.addProduct = addProduct;
        ctrl.updateVendors = updateVendors;
        ctrl.getProductTypeDescription = getProductTypeDescription;

        /** Check to see if this page should display user-specific products. */
        ctrl.isUserProducts = $state.current.name === 'userProducts';
        /** Show private products in list for foundation admin */
        ctrl.withPrivate = false;

        /** Properties for adding new products */
        ctrl.name = '';
        ctrl.description = '';
        ctrl.organizationId = '';

        // Should only be on user-products-page if authenticated.
        if (ctrl.isUserProducts && !$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.pageHeader = ctrl.isUserProducts ?
            'My Products' : 'Public Products';

        ctrl.pageParagraph = ctrl.isUserProducts ?
            'Your added products are listed here.' :
            'Public products are listed here.';

        if (ctrl.isUserProducts) {
            ctrl.authRequest = $scope.auth.doSignCheck()
                .then(ctrl.updateVendors)
                .then(ctrl.update);
        } else {
            ctrl.updateVendors();
            ctrl.update();
        }

        ctrl.rawData = null;
        ctrl.allVendors = {};
        ctrl.isAdminView = $rootScope.auth
                           && $rootScope.auth.currentUser
                           && $rootScope.auth.currentUser.is_admin;

        /**
         * This will contact the Refstack API to get a listing of products.
         */
        function update() {
            ctrl.showError = false;
            // Construct the API URL based on user-specified filters.
            var contentUrl = refstackApiUrl + '/products';
            if (typeof ctrl.rawData == 'undefined'
                    || ctrl.rawData === null) {
                ctrl.productsRequest =
                    $http.get(contentUrl).success(function (data) {
                        ctrl.rawData = data;
                        ctrl.updateData();
                    }).error(function (error) {
                        ctrl.rawData = null;
                        ctrl.showError = true;
                        ctrl.error =
                            'Error retrieving Products listing from server: ' +
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
            ctrl.data.products = ctrl.rawData.products.filter(function(s) {
                return ctrl._filterProduct(s); });
            ctrl.data.products.sort(function(a, b) {
                return a.name.localeCompare(b.name);
            });
        }

        /**
         * Returns true if a specific product can be displayed on this page.
         */
        function _filterProduct(product) {
            if (!ctrl.isUserProducts) {
                return product.public;
            }

            if ($rootScope.auth.currentUser.is_admin) {
                // TO-DO: filter out non-admin's items
                // because public is not a correct flag for this
                return product.public || ctrl.withPrivate;
            }

            return product.can_manage;
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
         * This will contact the Refstack API to get a listing of
         * available vendors that can be used to associate with products.
         */
        function updateVendors() {
            // Construct the API URL based on user-specified filters.
            var contentUrl = refstackApiUrl + '/vendors';
            ctrl.vendorsRequest =
                $http.get(contentUrl).success(function (data) {
                    ctrl.vendors = Array();
                    ctrl.allVendors = {};
                    data.vendors.forEach(function(vendor) {
                        ctrl.allVendors[vendor.id] = vendor;
                        if (vendor.can_manage) {
                            ctrl.vendors.push(vendor);
                        }
                    });
                    ctrl.vendors.sort(function(a, b) {
                        return a.name.localeCompare(b.name);
                    });
                    if (ctrl.vendors.length == 0) {
                        ctrl.vendors.push({name: 'Create New...', id: ''});
                    }
                    ctrl.organizationId = ctrl.vendors[0].id;
                }).error(function (error) {
                    ctrl.vendors = null;
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving vendor listing from server: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This will add new Product record.
         */
        function addProduct() {
            ctrl.showSuccess = false;
            ctrl.showError = false;
            var url = refstackApiUrl + '/products';
            var data = {
                name: ctrl.name,
                description: ctrl.description,
                organization_id: ctrl.organizationId,
                product_type: parseInt(ctrl.productType)
            };
            $http.post(url, data).success(function (data) {
                ctrl.rawData = null;
                ctrl.showSuccess = true;
                ctrl.name = '';
                ctrl.description = '';
                ctrl.productType = null;
                ctrl.update();
            }).error(function (error) {
                ctrl.showError = true;
                ctrl.error =
                    'Error adding new Product: ' + angular.toJson(error);
            });
        }
    }
})();
