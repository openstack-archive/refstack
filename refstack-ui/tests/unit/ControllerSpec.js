/** Jasmine specs for Refstack controllers */
describe('Refstack controllers', function () {
    'use strict';

    var fakeApiUrl = 'http://foo.bar/v1';
    beforeEach(function () {
        module(function ($provide) {
            $provide.constant('refstackApiUrl', fakeApiUrl);
        });
        module('refstackApp');
    });

    describe('headerController', function () {
        var scope, $location;

        beforeEach(inject(function ($rootScope, $controller, _$location_) {
            scope = $rootScope.$new();
            $location = _$location_;
            $controller('headerController', {$scope: scope});
        }));

        it('should set "navbarCollapsed" to true', function () {
            expect(scope.navbarCollapsed).toBe(true);
        });

        it('should have a function to check if the URL path is active',
            function () {
                $location.path('/');
                expect($location.path()).toBe('/');
                expect(scope.isActive('/')).toBe(true);
                expect(scope.isActive('/about')).toBe(false);

                $location.path('/results?cpid=123&foo=bar');
                expect($location.path()).toBe('/results?cpid=123&foo=bar');
                expect(scope.isActive('/results')).toBe(true);
            });
    });

    describe('authController', function () {
        var scope, $httpBackend, $window;

        beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            $window = {location: { href: jasmine.createSpy()} };
            $controller('authController', {$scope: scope, $window: $window});
        }));

        it('should show signin url for signed user', function () {
            $httpBackend.expectGET(fakeApiUrl +
            '/profile').respond({'openid': 'foo@bar.com',
                                 'email': 'foo@bar.com',
                                 'fullname': 'foo' });
            $httpBackend.flush();
            scope.doSignIn();
            expect($window.location.href).toBe(fakeApiUrl + '/auth/signin');
            expect(scope.isAuthenticated()).toBe(true);
        });

        it('should show signout url for not signed user', function () {
            $httpBackend.expectGET(fakeApiUrl +
            '/profile').respond(401);
            $httpBackend.flush();
            scope.doSignOut();
            expect($window.location.href).toBe(fakeApiUrl + '/auth/signout');
            expect(scope.isAuthenticated()).toBe(false);
        });
    });

    describe('capabilitiesController', function () {
        var scope, $httpBackend;

        beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            $controller('capabilitiesController', {$scope: scope});
        }));

        it('should set default states', function () {
            expect(scope.hideAchievements).toBe(true);
            expect(scope.hideTests).toBe(true);
            expect(scope.target).toBe('platform');
            expect(scope.status).toEqual({
                required: true, advisory: false,
                deprecated: false, removed: false
            });
        });

        it('should fetch the selected capabilities version and sort a ' +
           'program\'s capabilities into an object',
            function () {
                var fakeCaps = {
                    'schema': '1.3',
                    'platform': {'required': ['compute']},
                    'components': {
                        'compute': {
                            'required': ['cap_id_1'],
                            'advisory': ['cap_id_2'],
                            'deprecated': ['cap_id_3'],
                            'removed': ['cap_id_4']
                        }
                    }
                };

                $httpBackend.expectGET(fakeApiUrl +
                '/profile').respond(401);
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities').respond(['2015.03.json', '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities/2015.04.json').respond(fakeCaps);
                $httpBackend.flush();
                // The version list should be sorted latest first.
                expect(scope.versionList).toEqual(['2015.04.json',
                                                   '2015.03.json']);
                expect(scope.capabilities).toEqual(fakeCaps);
                var expectedTemplate = 'components/capabilities/partials/' +
                                       'capabilityDetailsV1.3.html';
                expect(scope.detailsTemplate).toEqual(expectedTemplate);
                var expectedTargetCaps = {
                    'cap_id_1': 'required',
                    'cap_id_2': 'advisory',
                    'cap_id_3': 'deprecated',
                    'cap_id_4': 'removed'
                };
                expect(scope.targetCapabilities).toEqual(expectedTargetCaps);
            });

        it('should have a function to check if a capability status is selected',
            function () {
                scope.targetCapabilities = {
                    'cap_id_1': 'required',
                    'cap_id_2': 'advisory',
                    'cap_id_3': 'deprecated',
                    'cap_id_4': 'removed'
                };

                // Expect only the required capability to return true.
                expect(scope.filterStatus({'id': 'cap_id_1'})).toBe(true);
                expect(scope.filterStatus({'id': 'cap_id_2'})).toBe(false);
                expect(scope.filterStatus({'id': 'cap_id_3'})).toBe(false);
                expect(scope.filterStatus({'id': 'cap_id_4'})).toBe(false);

                scope.status = {
                    required: true,
                    advisory: true,
                    deprecated: true,
                    removed: true
                };

                // Every capability should return true now.
                expect(scope.filterStatus({'id': 'cap_id_1'})).toBe(true);
                expect(scope.filterStatus({'id': 'cap_id_2'})).toBe(true);
                expect(scope.filterStatus({'id': 'cap_id_3'})).toBe(true);
                expect(scope.filterStatus({'id': 'cap_id_4'})).toBe(true);
            });

        it('should have a function to get the length of an object/dict',
            function () {
                var testObject = {
                    'test_id_1': {
                        'idempotent_id': 'id-1234'
                    },
                    'test_id_2': {
                        'idempotent_id': 'id-5678'
                    }
                };
                expect(scope.getObjectLength(testObject)).toBe(2);
            });
    });

    describe('resultsController', function () {
        var scope, $httpBackend;
        var fakeResponse = {
            'pagination': {'current_page': 1, 'total_pages': 2},
            'results': [{
                'created_at': '2015-03-09 01:23:45',
                'test_id': 'some-id',
                'cpid': 'some-cpid'
            }]
        };

        beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            scope = $rootScope.$new();
            $controller('resultsController', {$scope: scope});
        }));

        it('should fetch the first page of results with proper URL args',
            function () {
                // Initial results should be page 1 of all results.
                $httpBackend.expectGET(fakeApiUrl + '/profile').respond(401);
                $httpBackend.expectGET(fakeApiUrl +
                '/results?page=1').respond(fakeResponse);
                $httpBackend.flush();
                expect(scope.data).toEqual(fakeResponse);
                expect(scope.currentPage).toBe(1);

                // Simulate the user adding date filters.
                scope.startDate = new Date('2015-03-10T11:51:00');
                scope.endDate = new Date('2015-04-10T11:51:00');
                scope.update();
                $httpBackend.expectGET(fakeApiUrl +
                '/results?page=1' +
                '&start_date=2015-03-10 00:00:00' +
                '&end_date=2015-04-10 23:59:59')
                    .respond(fakeResponse);
                $httpBackend.flush();
                expect(scope.data).toEqual(fakeResponse);
                expect(scope.currentPage).toBe(1);
            });

        it('should set an error when results cannot be retrieved', function () {
            $httpBackend.expectGET(fakeApiUrl + '/profile').respond(401);
            $httpBackend.expectGET(fakeApiUrl + '/results?page=1').respond(404,
                {'detail': 'Not Found'});
            $httpBackend.flush();
            expect(scope.data).toBe(null);
            expect(scope.error).toEqual('Error retrieving results listing ' +
            'from server: {"detail":"Not Found"}');
            expect(scope.totalItems).toBe(0);
            expect(scope.showError).toBe(true);
        });

        it('should have an function to clear filters and update the view',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/profile').respond(401);
                $httpBackend.expectGET(fakeApiUrl +
                '/results?page=1').respond(fakeResponse);
                scope.startDate = 'some date';
                scope.endDate = 'some other date';
                scope.clearFilters();
                expect(scope.startDate).toBe(null);
                expect(scope.endDate).toBe(null);
                $httpBackend.expectGET(fakeApiUrl +
                '/results?page=1').respond(fakeResponse);
                $httpBackend.flush();
                expect(scope.data).toEqual(fakeResponse);
            });
    });

    describe('resultsReportController', function () {
        var scope, $httpBackend, stateparams;
        var fakeResultResponse = {'results': ['test_id_1']};
        var fakeCapabilityResponse = {
            'platform': {'required': ['compute']},
            'schema': '1.2',
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
                    'flagged': [ 'test_id_1'],
                    'tests': ['test_id_1', 'test_id_2']
                }
            }
        };

        beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
            $httpBackend = _$httpBackend_;
            stateparams = {testID: 1234};
            scope = $rootScope.$new();
            $controller('resultsReportController',
                {$scope: scope, $stateParams: stateparams});
        }));

        it('should make all necessary API requests to get results ' +
            'and capabilities',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/profile').respond(401);
                $httpBackend.expectGET(fakeApiUrl +
                '/results/1234').respond(fakeResultResponse);
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities').respond(['2015.03.json', '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities/2015.04.json').respond(fakeCapabilityResponse);
                $httpBackend.flush();
                expect(scope.resultsData).toEqual(fakeResultResponse);
                // The version list should be sorted latest first.
                expect(scope.versionList).toEqual(['2015.04.json',
                                                   '2015.03.json']);
                expect(scope.capabilityData).toEqual(fakeCapabilityResponse);
                expect(scope.schemaVersion).toEqual('1.2');
                expect(scope.detailsTemplate).toEqual('components/results-' +
                                                      'report/partials/' +
                                                      'reportDetailsV1.2.html');
            });

        it('should have a method that creates an object containing each ' +
           'relevant capability and its highest priority status',
            function () {
                scope.capabilityData = {
                    'schema': '1.3',
                    'platform': {'required': ['compute', 'object']},
                    'components': {
                        'compute': {
                            'required': ['cap_id_1'],
                            'advisory': ['cap_id_2'],
                            'deprecated': ['cap_id_3'],
                            'removed': []
                        },
                        'object': {
                            'required': ['cap_id_2'],
                            'advisory': ['cap_id_1', 'cap_id_3'],
                            'deprecated': [],
                            'removed': []
                        }
                    }
                };
                var expected = {
                    'cap_id_1': 'required',
                    'cap_id_2': 'required',
                    'cap_id_3': 'advisory'
                };
                expect(scope.getTargetCapabilitites()).toEqual(expected);
            });

        it('should be able to sort the results into a capability object for ' +
            'schema version 1.2',
            function () {
                scope.resultsData = fakeResultResponse;
                scope.capabilityData = fakeCapabilityResponse;
                scope.schemaVersion = '1.2';
                scope.buildCapabilitiesObject();
                var expectedCapsObject = {
                    'required': {
                        'caps': [{
                            'id': 'cap_id_1',
                            'passedTests': ['test_id_1'],
                            'notPassedTests': ['test_id_2'],
                            'passedFlagged': ['test_id_1'],
                            'notPassedFlagged': []
                        }],
                        'count': 2, 'passedCount': 1,
                        'flagFailCount': 0, 'flagPassCount': 1
                    },
                    'advisory': {'caps': [], 'count': 0, 'passedCount': 0,
                                 'flagFailCount': 0, 'flagPassCount': 0},
                    'deprecated': {'caps': [], 'count': 0, 'passedCount': 0,
                                   'flagFailCount': 0, 'flagPassCount': 0},
                    'removed': {'caps': [], 'count': 0, 'passedCount': 0,
                                'flagFailCount': 0, 'flagPassCount': 0}
                };
                expect(scope.caps).toEqual(expectedCapsObject);
                expect(scope.requiredPassPercent).toEqual(50);
                expect(scope.nonFlagPassCount).toEqual(0);
            });

        it('should be able to sort the results into a capability object for ' +
            'schema version 1.3',
            function () {
                scope.resultsData = fakeResultResponse;
                scope.capabilityData = {
                    'platform': {'required': ['compute']},
                    'schema': '1.3',
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
                            'tests': {
                                'test_id_1': {
                                    'flag': {
                                        'action': 'foo',
                                        'date': '2015-03-24',
                                        'reason': 'bar'
                                     },
                                    'idempotent_id': 'id-1234'
                                },
                                'test_id_2': {
                                    'idempotent_id': 'id-5678'
                                }
                            }
                        }
                    }
                };
                scope.schemaVersion = '1.3';
                scope.buildCapabilitiesObject();
                var expectedCapsObject = {
                    'required': {
                        'caps': [{
                            'id': 'cap_id_1',
                            'passedTests': ['test_id_1'],
                            'notPassedTests': ['test_id_2'],
                            'passedFlagged': ['test_id_1'],
                            'notPassedFlagged': []
                        }],
                        'count': 2, 'passedCount': 1,
                        'flagFailCount': 0, 'flagPassCount': 1
                    },
                    'advisory': {'caps': [], 'count': 0, 'passedCount': 0,
                                 'flagFailCount': 0, 'flagPassCount': 0},
                    'deprecated': {'caps': [], 'count': 0, 'passedCount': 0,
                                   'flagFailCount': 0, 'flagPassCount': 0},
                    'removed': {'caps': [], 'count': 0, 'passedCount': 0,
                                'flagFailCount': 0, 'flagPassCount': 0}
                };
                expect(scope.caps).toEqual(expectedCapsObject);
                expect(scope.requiredPassPercent).toEqual(50);
                expect(scope.nonFlagPassCount).toEqual(0);
            });
    });
});
