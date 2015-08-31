/**
 * Refstack Auth Failure Controller
 * This controller handles messages from Refstack API if user auth fails.
 */

var refstackApp = angular.module('refstackApp');

refstackApp.controller('authFailureController',
    [
        '$stateParams', '$state', 'raiseAlert',
        function($stateParams, $state, raiseAlert) {
            'use strict';
            raiseAlert('danger', 'Authentication Failure:',
                $stateParams.message);
            $state.go('home');
        }
    ]);
