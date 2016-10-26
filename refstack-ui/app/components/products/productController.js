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
        ctrl.getProductTests = getProductTests;
        ctrl.switchProductPublicity = switchProductPublicity;
        ctrl.associateTestMeta = associateTestMeta;
        ctrl.getGuidelineVersionList = getGuidelineVersionList;
        ctrl.addProductVersion = addProductVersion;
        ctrl.unassociateTest = unassociateTest;
        ctrl.openVersionModal = openVersionModal;
        ctrl.openProductEditModal = openProductEditModal;

        /** The product id extracted from the URL route. */
        ctrl.id = $stateParams.id;
        ctrl.productVersions = [];

        if (!$scope.auth.isAuthenticated) {
            $state.go('home');
        }

        /** Mappings of Interop WG components to marketing program names. */
        ctrl.targetMappings = {
            'platform': 'Openstack Powered Platform',
            'compute': 'OpenStack Powered Compute',
            'object': 'OpenStack Powered Object Storage'
        };

        // Pagination controls.
        ctrl.currentPage = 1;
        ctrl.itemsPerPage = 20;
        ctrl.maxSize = 5;

        ctrl.getProduct();
        ctrl.getProductVersions();
        ctrl.getProductTests();

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
                    ctrl.productProperties =
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

                    // Determine the null version.
                    for (var i = 0; i < data.length; i++) {
                        if (data[i].version === null) {
                            ctrl.nullVersion = data[i];
                            break;
                        }
                    }
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
         * Get tests runs associated with the current product.
         */
        function getProductTests() {
            ctrl.showTestsError = false;
            var content_url = refstackApiUrl + '/results' +
                '?page=' + ctrl.currentPage + '&product_id='
                + ctrl.id;

            ctrl.testsRequest = $http.get(content_url).success(
                function(data) {
                    ctrl.testsData = data.results;
                    ctrl.totalItems = data.pagination.total_pages *
                        ctrl.itemsPerPage;
                    ctrl.currentPage = data.pagination.current_page;
                }
            ).error(function(error) {
                ctrl.showTestsError = true;
                ctrl.testsError =
                    'Error retrieving tests from server: ' +
                    angular.toJson(error);
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
                    ctrl.productProperties = angular.fromJson(data.properties);
                }).error(function (error) {
                    raiseAlert('danger', 'Error: ', error.detail);
                });
        }

        /**
         * This will send an API request in order to associate a metadata
         * key-value pair with the given testId
         * @param {Number} index - index of the test object in the results list
         * @param {String} key - metadata key
         * @param {String} value - metadata value
         */
        function associateTestMeta(index, key, value) {
            var testId = ctrl.testsData[index].id;
            var metaUrl = [
                refstackApiUrl, '/results/', testId, '/meta/', key
            ].join('');

            var editFlag = key + 'Edit';
            if (value) {
                ctrl.associateRequest = $http.post(metaUrl, value)
                    .success(function () {
                        ctrl.testsData[index][editFlag] = false;
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            }
            else {
                ctrl.unassociateRequest = $http.delete(metaUrl)
                    .success(function () {
                        ctrl.testsData[index][editFlag] = false;
                    }).error(function (error) {
                        raiseAlert('danger', error.title, error.detail);
                    });
            }
        }

        /**
         * Retrieve an array of available capability files from the Refstack
         * API server, sort this array reverse-alphabetically, and store it in
         * a scoped variable.
         * Sample API return array: ["2015.03.json", "2015.04.json"]
         */
        function getGuidelineVersionList() {
            if (ctrl.versionList) {
                return;
            }
            var content_url = refstackApiUrl + '/guidelines';
            ctrl.versionsRequest =
                $http.get(content_url).success(function (data) {
                    ctrl.versionList = data.sort().reverse();
                }).error(function (error) {
                    raiseAlert('danger', error.title,
                               'Unable to retrieve version list');
                });
        }

        /**
         * Send a PUT request to the API server to unassociate a product with
         * a test result.
         */
        function unassociateTest(index) {
            var testId = ctrl.testsData[index].id;
            var url = refstackApiUrl + '/results/' + testId;
            ctrl.associateRequest = $http.put(url, {'product_version_id': null})
                .success(function () {
                    ctrl.testsData.splice(index, 1);
                }).error(function (error) {
                    raiseAlert('danger', error.title, error.detail);
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

        /**
         * This will open the modal that will allow product details
         * to be edited.
         */
        function openProductEditModal() {
            $uibModal.open({
                templateUrl: '/components/products/partials' +
                        '/productEditModal.html',
                backdrop: true,
                windowClass: 'modal',
                animation: true,
                controller: 'ProductEditModalController as modal',
                size: 'lg',
                resolve: {
                    product: function () {
                        return ctrl.product;
                    },
                    version: function () {
                        return ctrl.nullVersion;
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

        ctrl.version = angular.copy(version);
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
                // Update the original version object.
                version.cpid = ctrl.version.cpid;
                ctrl.showSuccess = true;
            }).error(function(error) {
                ctrl.showError = true;
                ctrl.error = error.detail;
            });
        }

    }

    angular
        .module('refstackApp')
        .controller('ProductEditModalController', ProductEditModalController);

    ProductEditModalController.$inject = [
        '$uibModalInstance', '$http', '$state', 'product',
        'version', 'refstackApiUrl'
    ];

    /**
     * Product Edit Modal Controller
     * This controls the modal that allows editing a product.
     */
    function ProductEditModalController($uibModalInstance, $http,
        $state, product, version, refstackApiUrl) {

        var ctrl = this;

        ctrl.close = close;
        ctrl.addField = addField;
        ctrl.saveChanges = saveChanges;
        ctrl.removeProperty = removeProperty;

        ctrl.product = angular.copy(product);
        ctrl.productName = product.name;
        ctrl.productProperties = [];
        ctrl.productVersion = angular.copy(version);
        ctrl.originalCpid = version ? version.cpid : null;

        parseProductProperties();

        /**
         * Close the product edit modal.
         */
        function close() {
            $uibModalInstance.dismiss('exit');
        }

        /**
         * Push a blank property key-value pair into the productProperties
         * array. This will spawn new input boxes.
         */
        function addField() {
            ctrl.productProperties.push({'key': '', 'value': ''});
        }

        /**
         * Send a PUT request to the server with the changes.
         */
        function saveChanges() {
            ctrl.showError = false;
            ctrl.showSuccess = false;
            var url = [refstackApiUrl, '/products/', ctrl.product.id].join('');
            var properties = propertiesToJson();
            var content = {'description': ctrl.product.description,
                           'properties': properties};
            if (ctrl.productName != ctrl.product.name) {
                content.name = ctrl.product.name;
            }

            // Request for product detail updating.
            $http.put(url, content).success(function() {

                // Request for product version CPID update if it has changed.
                if (ctrl.productVersion &&
                    ctrl.originalCpid !== ctrl.productVersion.cpid) {

                    url = url + '/versions/' + ctrl.productVersion.id;
                    content = {'cpid': ctrl.productVersion.cpid};
                    $http.put(url, content).success(function() {
                        ctrl.showSuccess = true;
                        ctrl.originalCpid = ctrl.productVersion.cpid;
                        $state.reload();
                    }).error(function(error) {
                        ctrl.showError = true;
                        ctrl.error = error.detail;
                    });
                }
                else {
                    ctrl.showSuccess = true;
                    $state.reload();
                }
            }).error(function(error) {
                ctrl.showError = true;
                ctrl.error = error.detail;
            });
        }

        /**
         * Remove a property from the productProperties array at the given
         * index.
         */
        function removeProperty(index) {
            ctrl.productProperties.splice(index, 1);
        }

        /**
         * Parse the product properties and put them in a format more suitable
         * for forms.
         */
        function parseProductProperties() {
            var props = angular.fromJson(ctrl.product.properties);
            angular.forEach(props, function(value, key) {
                ctrl.productProperties.push({'key': key, 'value': value});
            });
        }

        /**
         * Convert the list of property objects to a dict containing the
         * each key-value pair.
         */
        function propertiesToJson() {
            if (!ctrl.productProperties.length) {
                return null;
            }
            var properties = {};
            for (var i = 0, len = ctrl.productProperties.length; i < len; i++) {
                var prop = ctrl.productProperties[i];
                if (prop.key && prop.value) {
                    properties[prop.key] = prop.value;
                }
            }
            return properties;
        }
    }
})();
