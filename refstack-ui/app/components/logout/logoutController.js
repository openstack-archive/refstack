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
        .controller('LogoutController', LogoutController);

    LogoutController.$inject = [
        '$location', '$window', '$timeout'
    ];

    /**
     * Refstack Logout Controller
     * This controller handles logging out. In order to fully logout, the
     * openstackid_session cookie must also be removed. The way to do that
     * is to have the user's browser make a request to the openstackid logout
     * page. We do this by placing the logout link as the src for an html
     * image. After some time, the user is redirected home.
     */
    function LogoutController($location, $window, $timeout) {
        var ctrl = this;

        ctrl.openid_logout_url = $location.search().openid_logout;
        var img = new Image(0, 0);
        img.src = ctrl.openid_logout_url;
        ctrl.redirectWait = $timeout(function() {
            $window.location.href = '/';
        }, 500);
    }
})();
