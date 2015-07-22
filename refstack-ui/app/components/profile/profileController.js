/**
 * Refstack User Profile Controller
 * This controller handles user's profile page, where a user can view
 * account-specific information.
 */

var refstackApp = angular.module('refstackApp');

refstackApp.factory('PubKeys',
    ['$resource', 'refstackApiUrl', function($resource, refstackApiUrl) {
        'use strict';
        return $resource(refstackApiUrl + '/profile/pubkeys/:id', null, null);
    }]);

refstackApp.controller('profileController',
    [
        '$scope', '$http', 'refstackApiUrl', '$state', 'PubKeys',
        '$modal', 'raiseAlert',
        function($scope, $http, refstackApiUrl, $state,
                 PubKeys, $modal, raiseAlert) {
            'use strict';

            $scope.updatePubKeys = function (){
                var keys = PubKeys.query(function(){
                    $scope.pubkeys = [];
                    angular.forEach(keys, function (key) {
                        $scope.pubkeys.push({
                            'resource': key,
                            'format': key.format,
                            'shortKey': [
                                key.key.slice(0, 10),
                                '.',
                                key.key.slice(-10, -1)
                            ].join('.'),
                            'key': key.key,
                            'comment': key.comment
                        });
                    });
                });
            };
            $scope.openImportPubKeyModal = function () {
                $modal.open({
                    templateUrl: '/components/profile/importPubKeyModal.html',
                    backdrop: true,
                    windowClass: 'modal',
                    controller: 'importPubKeyModalController'
                }).result.finally(function() {
                    $scope.updatePubKeys();
                });
            };

            $scope.openShowPubKeyModal = function (pubKey) {
                $modal.open({
                    templateUrl: '/components/profile/showPubKeyModal.html',
                    backdrop: true,
                    windowClass: 'modal',
                    controller: 'showPubKeyModalController',
                    resolve: {
                        pubKey: function(){
                            return pubKey;
                        }
                    }
                }).result.finally(function() {
                    $scope.updatePubKeys();
                });
            };
            $scope.showRes = function(pubKey){
                raiseAlert('success', '', pubKey.key);
            };
            $scope.updatePubKeys();
        }
    ]);

refstackApp.controller('importPubKeyModalController',
    ['$scope', '$modalInstance', 'PubKeys', 'raiseAlert',
        function ($scope, $modalInstance, PubKeys, raiseAlert) {
            'use strict';
            $scope.importPubKey = function () {
                var newPubKey = new PubKeys(
                    {raw_key: $scope.raw_key,
                        self_signature: $scope.self_signature}
                );
                newPubKey.$save(function(newPubKey_){
                        raiseAlert('success',
                            '', 'Public key saved successfully');
                        $modalInstance.close(newPubKey_);
                    },
                    function(httpResp){
                        raiseAlert('danger',
                            httpResp.statusText, httpResp.data.title);
                        $scope.cancel();
                    }
                );
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }
    ]);

refstackApp.controller('showPubKeyModalController',
    ['$scope', '$modalInstance', 'raiseAlert', 'pubKey',
        function ($scope, $modalInstance, raiseAlert, pubKey) {
            'use strict';
            $scope.pubKey = pubKey.resource;
            $scope.rawKey = [pubKey.format,
                pubKey.key, pubKey.comment].join('\n');
            $scope.deletePubKey = function () {
                $scope.pubKey.$remove(
                    {id: $scope.pubKey.id},
                    function(){
                        raiseAlert('success',
                            '', 'Public key deleted successfully');
                        $modalInstance.close($scope.pubKey.id);
                    },
                    function(httpResp){
                        raiseAlert('danger',
                            httpResp.statusText, httpResp.data.title);
                        $scope.cancel();
                    }
                );
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }
    ]
);
