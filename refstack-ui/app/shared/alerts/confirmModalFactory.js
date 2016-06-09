(function () {
    'use strict';

    angular
        .module('refstackApp')
        .factory('confirmModal', confirmModal);

    confirmModal.$inject = ['$uibModal'];

    /**
     * Opens confirm modal dialog with input textbox
     */
    function confirmModal($uibModal) {
        return function(text, successHandler) {
            $uibModal.open({
                templateUrl: '/shared/alerts/confirmModal.html',
                controller: 'CustomConfirmModalController as confirmModal',
                size: 'md',
                resolve: {
                    data: function () {
                        return {
                            text: text,
                            successHandler: successHandler
                        };
                    }
                }
            });
        };
    }

    angular
        .module('refstackApp')
        .controller('CustomConfirmModalController',
                    CustomConfirmModalController);

    CustomConfirmModalController.$inject = ['$uibModalInstance', 'data'];

    /**
     * This is the controller for the alert pop-up.
     */
    function CustomConfirmModalController($uibModalInstance, data) {
        var ctrl = this;

        ctrl.confirm = confirm;
        ctrl.cancel = cancel;

        ctrl.data = angular.copy(data);

        /**
         * Initiate confirmation and call the success handler with the
         * input text.
         */
        function confirm() {
            $uibModalInstance.close();
            if (angular.isDefined(ctrl.data.successHandler)) {
                ctrl.data.successHandler(ctrl.inputText);
            }
        }

        /**
         * Close the confirm modal without initiating changes.
         */
        function cancel() {
            $uibModalInstance.dismiss('cancel');
        }
    }
})();
