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
        var scope, ctrl, $httpBackend, refstackApiUrl;
        var fakeApiUrl = "http://foo.bar/v1";
        beforeEach(function() {
            module('refstackApp');
            module(function($provide) {
                $provide.constant('refstackApiUrl', fakeApiUrl);
            });
        });

        beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            ctrl = $controller('capabilitiesController', {$scope: scope});
        }));

        it('should set default states', function() {
            expect(scope.hideAchievements).toBe(true);
            expect(scope.hideTests).toBe(true);
            expect(scope.target).toBe('platform');
            expect(scope.status).toEqual({required: 'required', advisory: '',
                                          deprecated: '', removed: ''});
        });

        it('should fetch the selected capabilities version', function() {
            $httpBackend.expectGET(fakeApiUrl+'/capabilities').respond(['2015.03.json', '2015.04.json']);
            // Should call request with latest version.
            $httpBackend.expectGET(fakeApiUrl+'/capabilities/2015.04.json').respond({'foo': 'bar'});
            $httpBackend.flush();
            // The version list should be sorted latest first.
            expect(scope.versionList).toEqual(['2015.04.json', '2015.03.json']);
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

    describe('resultsController', function() {
        var scope, ctrl, $httpBackend, refstackApiUrl;
        var fakeApiUrl = "http://foo.bar/v1";
        var fakeResponse = {'pagination': {'current_page': 1, 'total_pages': 2},
                            'results': [{'created_at': '2015-03-09 01:23:45',
                                         'test_id': 'some-id',
                                         'cpid': 'some-cpid'}]};

        beforeEach(function() {
            module('refstackApp');
            module(function($provide) {
                $provide.constant('refstackApiUrl', fakeApiUrl);
            });
        });

        beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            ctrl = $controller('resultsController', {$scope: scope});
        }));

        it('should fetch the first page of results with proper URL args', function() {
            // Initial results should be page 1 of all results.
            $httpBackend.expectGET(fakeApiUrl+'/results?page=1').respond(fakeResponse);
            $httpBackend.flush();
            expect(scope.data).toEqual(fakeResponse);
            expect(scope.currentPage).toBe(1);

            // Simulate the user adding date filters.
            scope.startDate = new Date('2015-03-10T11:51:00');
            scope.endDate = new Date('2015-04-10T11:51:00');
            scope.update();
            $httpBackend.expectGET(fakeApiUrl+'/results?page=1&start_date=2015-03-10 00:00:00&end_date=2015-04-10 23:59:59').respond(fakeResponse);
            $httpBackend.flush();
            expect(scope.data).toEqual(fakeResponse);
            expect(scope.currentPage).toBe(1);
        });

        it('should set an error when results cannot be retrieved', function() {
            $httpBackend.expectGET(fakeApiUrl+'/results?page=1').respond(404, {'detail': 'Not Found'});
            $httpBackend.flush();
            expect(scope.data).toBe(null);
            expect(scope.error).toEqual('Error retrieving results listing from server: {"detail":"Not Found"}');
            expect(scope.totalItems).toBe(0);
            expect(scope.showError).toBe(true);
        });

        it('should have an function to clear filters and update the view', function() {
            $httpBackend.expectGET(fakeApiUrl+'/results?page=1').respond(fakeResponse);
            scope.startDate = "some date";
            scope.endDate = "some other date";
            scope.clearFilters();
            expect(scope.startDate).toBe(null);
            expect(scope.endDate).toBe(null);
            $httpBackend.expectGET(fakeApiUrl+'/results?page=1').respond(fakeResponse);
            $httpBackend.flush();
            expect(scope.data).toEqual(fakeResponse);
        });
    });

    describe('resultsReportController', function() {
        var scope, ctrl, $httpBackend, refstackApiUrl, stateparams;
        var fakeApiUrl = "http://foo.bar/v1";
        var fakeResultResponse = {'results': ['test_id_1']}
        var fakeCapabilityResponse = {'platform': {'required': ['compute']},
                                      'components': {
                                          'compute': {
                                              'required': ['cap_id_1'],
                                              'advisory': [],
                                              'deprecated': [],
                                              'removed': []
                                           }
                                       },
                                       'capabilities': {
                                           'cap_id_1': {
                                               'status': 'required',
                                               'flagged': [],
                                               'tests': ['test_id_1', 'test_id_2']
                                            }
                                        }
                                      };

        beforeEach(function() {
            module('refstackApp');
            module(function($provide) {
                $provide.constant('refstackApiUrl', fakeApiUrl);
            });
        });

        beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            stateparams = {testID: 1234};
            scope = $rootScope.$new();
            ctrl = $controller('resultsReportController', {$scope: scope, $stateParams: stateparams});
        }));

        it('should make all necessary API requests to get results and capabilities', function() {
            $httpBackend.expectGET(fakeApiUrl+'/results/1234').respond(fakeResultResponse);
            $httpBackend.expectGET(fakeApiUrl+'/capabilities').respond(['2015.03.json', '2015.04.json']);
            // Should call request with latest version.
            $httpBackend.expectGET(fakeApiUrl+'/capabilities/2015.04.json').respond(fakeCapabilityResponse);
            $httpBackend.flush();
            expect(scope.resultsData).toEqual(fakeResultResponse);
            // The version list should be sorted latest first.
            expect(scope.versionList).toEqual(['2015.04.json', '2015.03.json']);
            expect(scope.capabilityData).toEqual(fakeCapabilityResponse);
        });

        it('should be able to sort the results into a capability object', function() {
            scope.resultsData = fakeResultResponse;
            scope.capabilityData = fakeCapabilityResponse;
            scope.buildCapabilityObject();
            var expectedCapsObject = {'required': {'caps': [{'id': 'cap_id_1',
                                                              'passedTests': ['test_id_1'],
                                                              'notPassedTests': ['test_id_2']}],
                                                    'count': 2, 'passedCount': 1},
                                      'advisory': {'caps': [], 'count': 0, 'passedCount': 0},
                                      'deprecated': {'caps': [], 'count': 0, 'passedCount': 0},
                                      'removed': {'caps': [], 'count': 0, 'passedCount': 0}};
            expect(scope.caps).toEqual(expectedCapsObject);
        });
    });
});
