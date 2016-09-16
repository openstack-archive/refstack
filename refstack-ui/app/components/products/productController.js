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
        '$scope', '$http', '$state', '$stateParams', '$window', '$uibModal',
        'refstackApiUrl', 'raiseAlert'
    ];

    /**
     * RefStack Product Controller
     * This controller is for the '/product/' details page where owner can
     * view details of the product.
     */
    function ProductController($scope, $http, $state, $stateParams,
            $window, $uibModal, refstackApiUrl, raiseAlert) {
        var ctrl = this;

        ctrl.getProduct = getProduct;
        ctrl.getProductVersions = getProductVersions;
        ctrl.deleteProduct = deleteProduct;
        ctrl.deleteProductVersion = deleteProductVersion;
        ctrl.switchProductPublicity = switchProductPublicity;
        ctrl.addProductVersion = addProductVersion;
        ctrl.openVersionModal = openVersionModal;

        /** The product id extracted from the URL route. */
        ctrl.id = $stateParams.id;
        ctrl.productVersions = [];

        if (!$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        ctrl.getProduct();
        ctrl.getProductVersions();

        /**
         * This will contact the Refstack API to get a product information.
         */
        function getProduct() {
            ctrl.showError = false;
            ctrl.product = null;
            var content_url = refstackApiUrl + '/products/' + ctrl.id;
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
         * This will contact the Refstack API to get product versions.
         */
        function getProductVersions() {
            ctrl.showError = false;
            var content_url = refstackApiUrl + '/products/' + ctrl.id +
                '/versions';
            ctrl.productVersionsRequest = $http.get(content_url).success(
                function(data) {
                    ctrl.productVersions = data;
                }
            ).error(function(error) {
                ctrl.showError = true;
                ctrl.error =
                    'Error retrieving versions from server: ' +
                    angular.toJson(error);
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
         * This will delete the given product versions.
         */
        function deleteProductVersion(versionId) {
            var url = [
                refstackApiUrl, '/products/', ctrl.id,
                '/versions/', versionId ].join('');
            $http.delete(url).success(function () {
                ctrl.getProductVersions();
            }).error(function (error) {
                raiseAlert('danger', 'Error: ', error.detail);
            });
        }

        /**
         * Set a POST request to the API server to add a new version for
         * the product.
         */
        function addProductVersion() {
            var url = [refstackApiUrl, '/products/', ctrl.id,
                '/versions'].join('');
            ctrl.addVersionRequest = $http.post(url,
                {'version': ctrl.newProductVersion})
                .success(function (data) {
                    ctrl.productVersions.push(data);
                    ctrl.newProductVersion = '';
                    ctrl.showNewVersionInput = false;
                }).error(function (error) {
                    raiseAlert('danger', error.title, error.detail);
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

        /**
         * This will open the modal that will allow a product version
         * to be managed.
         */
        function openVersionModal(version) {
            $uibModal.open({
                templateUrl: '/components/products/partials' +
                        '/versionsModal.html',
                backdrop: true,
                windowClass: 'modal',
                animation: true,
                controller: 'ProductVersionModalController as modal',
                size: 'lg',
                resolve: {
                    version: function () {
                        return version;
                    },
                    parent: function () {
                        return ctrl;
                    }
                }
            });
        }
    }

    angular
        .module('refstackApp')
        .controller('ProductVersionModalController',
                    ProductVersionModalController);

    ProductVersionModalController.$inject = [
        '$uibModalInstance', '$http', 'refstackApiUrl', 'version', 'parent'
    ];

    /**
     * Product Version Modal Controller
     * This controller is for the modal that appears if a user wants to
     * manage a product version.
     */
    function ProductVersionModalController($uibModalInstance, $http,
        refstackApiUrl, version, parent) {

        var ctrl = this;

        ctrl.version = version;
        ctrl.parent = parent;

        ctrl.close = close;
        ctrl.deleteProductVersion = deleteProductVersion;
        ctrl.saveChanges = saveChanges;

        /**
         * This function will close/dismiss the modal.
         */
        function close() {
            $uibModalInstance.dismiss('exit');
        }

        /**
         * Call the parent function to delete a version, then close the modal.
         */
        function deleteProductVersion() {
            ctrl.parent.deleteProductVersion(ctrl.version.id);
            ctrl.close();
        }

        /**
         * This will update the current version, saving changes.
         */
        function saveChanges() {
            ctrl.showSuccess = false;
            ctrl.showError = false;
            var url = [
                refstackApiUrl, '/products/', ctrl.version.product_id,
                '/versions/', ctrl.version.id ].join('');
            var content = {'cpid': ctrl.version.cpid};
            $http.put(url, content).success(function() {
                ctrl.showSuccess = true;
            }).error(function(error) {
                ctrl.showError = true;
                ctrl.error = error.detail;
            });
        }

    }
})();
