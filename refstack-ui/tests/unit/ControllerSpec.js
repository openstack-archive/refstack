'use strict';

/* Jasmine specs for Refstack controllers */
describe('Refstack controllers', function() {

    describe('headerController', function() {
        var scope, ctrl, $location;
        beforeEach(module('refstackApp'));

        beforeEach(inject(function($rootScope, $controller, _$location_) {
            scope = $rootScope.$new();
            $location = _$location_;
            ctrl = $controller('headerController', {$scope: scope});
        }));

        it('should set "navbarCollapsed" to true', function() {
            expect(scope.navbarCollapsed).toBe(true);
        });

        it('should have a function to check if the URL path is active', function() {
            $location.path('/');
            expect($location.path()).toBe('/');
            expect(scope.isActive('/')).toBe(true);
            expect(scope.isActive('/about')).toBe(false);

            $location.path('/results?cpid=123&foo=bar');
            expect($location.path()).toBe('/results?cpid=123&foo=bar');
            expect(scope.isActive('/results')).toBe(true);
        });
    });

    describe('capabilitiesController', function() {
        var scope, ctrl, $httpBackend;
        beforeEach(module('refstackApp'));

        beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            ctrl = $controller('capabilitiesController', {$scope: scope});
        }));

        it('should set default states', function() {
            expect(scope.hideAchievements).toBe(true);
            expect(scope.hideTests).toBe(true);
            expect(scope.version).toBe('2015.03');
            expect(scope.target).toBe('platform');
            expect(scope.status).toEqual({required: 'required', advisory: '',
                                          deprecated: '', removed: ''});

        });

        it('should fetch the selected capabilities version', function() {
            $httpBackend.expectGET('assets/capabilities/2015.03.json').respond({'foo': 'bar'});
            $httpBackend.flush();
            expect(scope.capabilities).toEqual({'foo': 'bar'});
        });

        it('should have a function to check if a status filter is selected', function() {
            expect(scope.filterStatus({'status': 'required'})).toBe(true);
            expect(scope.filterStatus({'status': 'advisory'})).toBe(false);
            expect(scope.filterStatus({'status': 'deprecated'})).toBe(false);
            expect(scope.filterStatus({'status': 'removed'})).toBe(false);

            scope.status = {
                required: 'required',
                advisory: 'advisory',
                deprecated: 'deprecated',
                removed: 'removed'
            };

            expect(scope.filterStatus({'status': 'required'})).toBe(true);
            expect(scope.filterStatus({'status': 'advisory'})).toBe(true);
            expect(scope.filterStatus({'status': 'deprecated'})).toBe(true);
            expect(scope.filterStatus({'status': 'removed'})).toBe(true);
        });

        it('should have a function to check if a capability belongs to a program', function() {
            scope.capabilities =  {'platform': {'required': ['compute']},
                                   'components': {
                                       'compute': {
                                           'required': ['cap_id_1'],
                                           'advisory': ['cap_id_2'],
                                           'deprecated': ['cap_id_3'],
                                           'removed': ['cap_id_4']
                                       }
                                   }};
            expect(scope.filterProgram({'id': 'cap_id_1'})).toBe(true);
            expect(scope.filterProgram({'id': 'cap_id_2'})).toBe(true);
            expect(scope.filterProgram({'id': 'cap_id_3'})).toBe(true);
            expect(scope.filterProgram({'id': 'cap_id_4'})).toBe(true);
            expect(scope.filterProgram({'id': 'cap_id_5'})).toBe(false);
        });
    });
});
