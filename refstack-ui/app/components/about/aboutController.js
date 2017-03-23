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
        .controller('AboutController', AboutController);

    AboutController.$inject = ['$location'];

    /**
     * RefStack About Controller
     * This controller handles the about page and the multiple templates
     * associated to the page.
     */
    function AboutController($location) {
        var ctrl = this;

        ctrl.selectOption = selectOption;
        ctrl.getHash = getHash;

        ctrl.options = {
            'about' : {
                'title': 'About RefStack',
                'template': 'components/about/templates/README.html',
                'order': 1
            },
            'uploading-your-results': {
                'title': 'Uploading Your Results',
                'template': 'components/about/templates/' +
                            'uploading_private_results.html',
                'order': 2
            },
            'managing-results': {
                'title': 'Managing Results',
                'template': 'components/about/templates/' +
                            'test_result_management.html',
                'order': 3
            },
            'vendors-and-products': {
                'title': 'Vendors and Products',
                'template': 'components/about/templates/vendor_product.html',
                'order': 4
            }
        };

        /**
         * Given an option key, mark it as selected and set the corresponding
         * template and URL hash.
         */
        function selectOption(key) {
            ctrl.selected = key;
            ctrl.template = ctrl.options[key].template;
            $location.hash(key);
        }

        /**
         * Get the hash in the URL and select it if possible.
         */
        function getHash() {
            var hash = $location.hash();
            if (hash && hash in ctrl.options) {
                ctrl.selectOption(hash);
            }
            else {
                ctrl.selectOption('about');
            }
        }

        ctrl.getHash();
    }
})();
