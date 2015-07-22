var refstackApp = angular.module('refstackApp');

refstackApp.factory('raiseAlert',
    ['$modal', function($modal) {
        'use strict';
        return function(mode, title, text) {
            $modal.open({
                templateUrl: '/shared/alerts/alertModal.html',
                controller: 'raiseAlertModalController',
                backdrop: true,
                keyboard: true,
                backdropClick: true,
                size: 'md',
                resolve: {
                    data: function () {
                        return {
                            mode: mode,
                            title: title,
                            text: text
                        };
                    }
                }
            });
        };
    }]
);


refstackApp.controller('raiseAlertModalController',
    ['$scope', '$modalInstance', '$interval', 'data',
        function ($scope, $modalInstance, $interval, data) {
            'use strict';
            $scope.data = data;
            $scope.close = function() {
                $modalInstance.close();
            };
            $interval(function(){
                $scope.close();
            }, 3000, 1);
        }
    ]
);
