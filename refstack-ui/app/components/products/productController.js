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
        .controller('ProductController', ProductController);

    ProductController.$inject = [
        '$scope', '$http', '$state', '$stateParams', '$window',
        'refstackApiUrl', 'raiseAlert'
    ];

    /**
     * RefStack Product Controller
     * This controller is for the '/product/' details page where owner can
     * view details of the product.
     */
    function ProductController($scope, $http, $state, $stateParams,
            $window, refstackApiUrl, raiseAlert) {
        var ctrl = this;

        ctrl.getProduct = getProduct;
        ctrl.deleteProduct = deleteProduct;
        ctrl.switchProductPublicity = switchProductPublicity;

        /** The product id extracted from the URL route. */
        ctrl.id = $stateParams.id;

        if (!$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.getProduct();

        /**
         * This will contact the Refstack API to get a product information.
         */
        function getProduct() {
            ctrl.showError = false;
            ctrl.product = null;
            // Construct the API URL based on user-specified filters.
            var content_url = refstackApiUrl + '/products/' + ctrl.id;
            ctrl.productRequest =
                ctrl.productRequest = $http.get(content_url).success(
                    function(data) {
                        ctrl.product = data;
                        ctrl.product_properties =
                            angular.fromJson(data.properties);
                    }
                ).error(function(error) {
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving from server: ' +
                        angular.toJson(error);
                }).then(function() {
                    var url = refstackApiUrl + '/vendors/' +
                        ctrl.product.organization_id;
                    $http.get(url).success(function(data) {
                        ctrl.vendor = data;
                    }).error(function(error) {
                        ctrl.showError = true;
                        ctrl.error =
                            'Error retrieving from server: ' +
                            angular.toJson(error);
                    });
                });
        }

        /**
         * This will delete the product.
         */
        function deleteProduct() {
            var url = [refstackApiUrl, '/products/', ctrl.id].join('');
            $http.delete(url).success(function () {
                $window.location.href = '/';
            }).error(function (error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * This will switch public/private property of the product.
         */
        function switchProductPublicity() {
            var url = [refstackApiUrl, '/products/', ctrl.id].join('');
            $http.put(url, {public: !ctrl.product.public}).success(
                function (data) {
                    ctrl.product = data;
                    ctrl.product_properties = angular.fromJson(data.properties);
                }).error(function (error) {
                    raiseAlert('danger', 'Error: ', error.detail);
                });
        }
    }
})();
