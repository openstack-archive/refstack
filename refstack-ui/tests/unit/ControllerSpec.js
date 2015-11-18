/** Jasmine specs for Refstack controllers */
describe('Refstack controllers', function () {
    'use strict';

    var fakeApiUrl = 'http://foo.bar/v1';
    var $httpBackend;
    beforeEach(function () {
        module(function ($provide) {
            $provide.constant('refstackApiUrl', fakeApiUrl);
        });
        module('refstackApp');
        inject(function(_$httpBackend_) {
            $httpBackend = _$httpBackend_;
        });
        $httpBackend.whenGET(fakeApiUrl + '/profile').respond(401);
        $httpBackend.whenGET('/components/home/home.html')
            .respond('<div>mock template</div>');
    });

    describe('HeaderController', function () {
        var $location, ctrl;

        beforeEach(inject(function ($controller, _$location_) {
            $location = _$location_;
            ctrl = $controller('HeaderController', {});
        }));

        it('should set "navbarCollapsed" to true', function () {
            expect(ctrl.navbarCollapsed).toBe(true);
        });

        it('should have a function to check if the URL path is active',
            function () {
                $location.path('/');
                expect($location.path()).toBe('/');
                expect(ctrl.isActive('/')).toBe(true);
                expect(ctrl.isActive('/about')).toBe(false);

                $location.path('/results?cpid=123&foo=bar');
                expect($location.path()).toBe('/results?cpid=123&foo=bar');
                expect(ctrl.isActive('/results')).toBe(true);
            });
    });

    describe('LogoutController', function () {
        var $location, ctrl;

        beforeEach(inject(function ($controller, _$location_) {
            $location = _$location_;
            $location.url('/logout?openid_logout=some_url');
            ctrl = $controller('LogoutController', {});
        }));

        it('should set the openID logout URL based on query string',
            function () {
                expect($location.url()).toBe('/logout?openid_logout=some_url');
                expect(ctrl.openid_logout_url).toBe('some_url');
            });
    });

    describe('CapabilitiesController', function () {
        var ctrl;

        beforeEach(inject(function ($controller) {
            ctrl = $controller('CapabilitiesController', {});
        }));

        it('should set default states', function () {
            expect(ctrl.target).toBe('platform');
            expect(ctrl.status).toEqual({
                required: true, advisory: false,
                deprecated: false, removed: false
            });
        });

        it('should fetch the selected capabilities version and sort a ' +
           'program\'s capabilities into an object',
            function () {
                var fakeCaps = {
                    'schema': '1.3',
                    'status': 'approved',
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
                '/capabilities').respond(['2015.03.json', '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities/2015.04.json').respond(fakeCaps);
                $httpBackend.flush();
                // The version list should be sorted latest first.
                expect(ctrl.versionList).toEqual(['2015.04.json',
                                                   '2015.03.json']);
                expect(ctrl.capabilities).toEqual(fakeCaps);
                // The guideline status should be approved.
                expect(ctrl.capabilities.status).toEqual('approved');
                var expectedTargetCaps = {
                    'cap_id_1': 'required',
                    'cap_id_2': 'advisory',
                    'cap_id_3': 'deprecated',
                    'cap_id_4': 'removed'
                };
                expect(ctrl.targetCapabilities).toEqual(expectedTargetCaps);
            });

        it('should have a function to check if a capability status is selected',
            function () {
                ctrl.targetCapabilities = {
                    'cap_id_1': 'required',
                    'cap_id_2': 'advisory',
                    'cap_id_3': 'deprecated',
                    'cap_id_4': 'removed'
                };

                // Expect only the required capability to return true.
                expect(ctrl.filterStatus({'id': 'cap_id_1'})).toBe(true);
                expect(ctrl.filterStatus({'id': 'cap_id_2'})).toBe(false);
                expect(ctrl.filterStatus({'id': 'cap_id_3'})).toBe(false);
                expect(ctrl.filterStatus({'id': 'cap_id_4'})).toBe(false);

                ctrl.status = {
                    required: true,
                    advisory: true,
                    deprecated: true,
                    removed: true
                };

                // Every capability should return true now.
                expect(ctrl.filterStatus({'id': 'cap_id_1'})).toBe(true);
                expect(ctrl.filterStatus({'id': 'cap_id_2'})).toBe(true);
                expect(ctrl.filterStatus({'id': 'cap_id_3'})).toBe(true);
                expect(ctrl.filterStatus({'id': 'cap_id_4'})).toBe(true);
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
                expect(ctrl.getObjectLength(testObject)).toBe(2);
            });
    });

    describe('resultsController', function () {
        var scope, ctrl;
        var fakeResponse = {
            'pagination': {'current_page': 1, 'total_pages': 2},
            'results': [{
                'created_at': '2015-03-09 01:23:45',
                'test_id': 'some-id',
                'cpid': 'some-cpid'
            }]
        };

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            ctrl = $controller('ResultsController', {$scope: scope});
        }));

        it('should fetch the first page of results with proper URL args',
            function () {
                // Initial results should be page 1 of all results.
                $httpBackend.expectGET(fakeApiUrl + '/results?page=1')
                    .respond(fakeResponse);
                $httpBackend.flush();
                expect(ctrl.data).toEqual(fakeResponse);
                expect(ctrl.currentPage).toBe(1);

                // Simulate the user adding date filters.
                ctrl.startDate = new Date('2015-03-10T11:51:00');
                ctrl.endDate = new Date('2015-04-10T11:51:00');
                ctrl.update();
                $httpBackend.expectGET(fakeApiUrl +
                '/results?page=1' +
                '&start_date=2015-03-10 00:00:00' +
                '&end_date=2015-04-10 23:59:59')
                    .respond(fakeResponse);
                $httpBackend.flush();
                expect(ctrl.data).toEqual(fakeResponse);
                expect(ctrl.currentPage).toBe(1);
            });

        it('should set an error when results cannot be retrieved', function () {
            $httpBackend.expectGET(fakeApiUrl + '/results?page=1').respond(404,
                {'detail': 'Not Found'});
            $httpBackend.flush();
            expect(ctrl.data).toBe(null);
            expect(ctrl.error).toEqual('Error retrieving results listing ' +
            'from server: {"detail":"Not Found"}');
            expect(ctrl.totalItems).toBe(0);
            expect(ctrl.showError).toBe(true);
        });

        it('should have an function to clear filters and update the view',
            function () {
                ctrl.startDate = 'some date';
                ctrl.endDate = 'some other date';
                ctrl.clearFilters();
                expect(ctrl.startDate).toBe(null);
                expect(ctrl.endDate).toBe(null);
            });
    });

    describe('ResultsReportController', function () {
        var stateparams, ctrl;
        var fakeResultResponse = {'results': ['test_id_1']};
        var fakeCapabilityResponse = {
            'platform': {'required': ['compute']},
            'schema': '1.2',
            'status': 'approved',
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

        beforeEach(inject(function ($controller) {
            stateparams = {testID: 1234};
            ctrl = $controller('ResultsReportController',
                {$stateParams: stateparams}
            );
        }));

        it('should make all necessary API requests to get results ' +
            'and capabilities',
            function () {
                $httpBackend.expectGET(fakeApiUrl +
                '/results/1234').respond(fakeResultResponse);
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities').respond(['2015.03.json', '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/capabilities/2015.04.json').respond(fakeCapabilityResponse);
                $httpBackend.flush();
                expect(ctrl.resultsData).toEqual(fakeResultResponse);
                // The version list should be sorted latest first.
                expect(ctrl.versionList).toEqual(['2015.04.json',
                                                   '2015.03.json']);
                expect(ctrl.capabilityData).toEqual(fakeCapabilityResponse);
                // The guideline status should be approved.
                expect(ctrl.capabilityData.status).toEqual('approved');
                expect(ctrl.schemaVersion).toEqual('1.2');
            });

        it('should have a method that creates an object containing each ' +
           'relevant capability and its highest priority status',
            function () {
                ctrl.capabilityData = {
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
                expect(ctrl.getTargetCapabilities()).toEqual(expected);
            });

        it('should be able to sort the results into a capability object for ' +
            'schema version 1.2',
            function () {
                ctrl.resultsData = fakeResultResponse;
                ctrl.capabilityData = fakeCapabilityResponse;
                ctrl.schemaVersion = '1.2';
                ctrl.buildCapabilitiesObject();
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
                expect(ctrl.caps).toEqual(expectedCapsObject);
                expect(ctrl.requiredPassPercent).toEqual(50);
                expect(ctrl.nonFlagPassCount).toEqual(0);
            });

        it('should be able to sort the results into a capability object for ' +
            'schema version 1.3 and above',
            function () {
                ctrl.resultsData = {'results': ['test_id_1',
                                                'old_test_id_3',
                                                'test_id_4']
                                   };
                ctrl.capabilityData = {
                    'platform': {'required': ['compute']},
                    'schema': '1.4',
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
                                    'flagged': {
                                        'action': 'foo',
                                        'date': '2015-03-24',
                                        'reason': 'bar'
                                    },
                                    'idempotent_id': 'id-1234'
                                },
                                'test_id_2': {
                                    'idempotent_id': 'id-5678'
                                },
                                'test_id_3': {
                                    'idempotent_id': 'id-5679',
                                    'aliases': ['old_test_id_3']
                                },
                                'test_id_4': {
                                    'idempotent_id': 'id-5680'
                                }
                            }
                        }
                    }
                };
                ctrl.schemaVersion = '1.4';
                ctrl.buildCapabilitiesObject();
                var expectedCapsObject = {
                    'required': {
                        'caps': [{
                            'id': 'cap_id_1',
                            'passedTests': ['test_id_1',
                                            'test_id_3',
                                            'test_id_4'],
                            'notPassedTests': ['test_id_2'],
                            'passedFlagged': ['test_id_1'],
                            'notPassedFlagged': []
                        }],
                        'count': 4, 'passedCount': 3,
                        'flagFailCount': 0, 'flagPassCount': 1
                    },
                    'advisory': {'caps': [], 'count': 0, 'passedCount': 0,
                                 'flagFailCount': 0, 'flagPassCount': 0},
                    'deprecated': {'caps': [], 'count': 0, 'passedCount': 0,
                                   'flagFailCount': 0, 'flagPassCount': 0},
                    'removed': {'caps': [], 'count': 0, 'passedCount': 0,
                                'flagFailCount': 0, 'flagPassCount': 0}
                };
                expect(ctrl.caps).toEqual(expectedCapsObject);
                expect(ctrl.requiredPassPercent).toEqual(75);
                expect(ctrl.nonFlagPassCount).toEqual(2);
            });

        it('should have a method to determine if a test is flagged',
            function () {
                var capObj = {'flagged': [ 'test1'],
                              'tests': ['test1', 'test2']};

                ctrl.schemaVersion = '1.2';
                expect(ctrl.isTestFlagged('test1', capObj)).toEqual(true);
                expect(ctrl.isTestFlagged('test2', capObj)).toEqual(false);

                capObj = {
                    'tests': {
                        'test1': {
                            'flagged': {
                                'action': 'foo',
                                'date': '2015-03-24',
                                'reason': 'bar'
                            },
                            'idempotent_id': 'id-1234'
                        },
                        'test2': {
                            'idempotent_id': 'id-5678'
                        }
                    }
                };

                ctrl.schemaVersion = '1.3';
                expect(ctrl.isTestFlagged('test1', capObj)).toBeTruthy();
                expect(ctrl.isTestFlagged('test2', capObj)).toBeFalsy();

                expect(ctrl.isTestFlagged('test2', null)).toEqual(false);
            });

        it('should have a method to get the reason a flagged test is flagged',
            function () {
                var capObj = {'flagged': [ 'test1'],
                              'tests': ['test1', 'test2']};

                ctrl.schemaVersion = '1.2';
                expect(ctrl.getFlaggedReason('test1', capObj)).toEqual(
                    'DefCore has flagged this test.');

                // Check that non-flagged test returns empty string.
                expect(ctrl.getFlaggedReason('test2', capObj)).toEqual('');

                capObj = {
                    'tests': {
                        'test1': {
                            'flagged': {
                                'action': 'foo',
                                'date': '2015-03-24',
                                'reason': 'bar'
                            },
                            'idempotent_id': 'id-1234'
                        }
                    }
                };

                ctrl.schemaVersion = '1.3';
                expect(ctrl.getFlaggedReason('test1', capObj)).toEqual('bar');
            });

        it('should have a method to determine whether a capability should ' +
           'be shown',
            function () {
                var caps = [{'id': 'cap_id_1',
                             'passedTests': ['test_id_1'],
                             'notPassedTests': [],
                             'passedFlagged': ['test_id_1'],
                             'notPassedFlagged': []
                            },
                            {'id': 'cap_id_2',
                             'passedTests': [],
                             'notPassedTests': ['test_id_4'],
                             'passedFlagged': [],
                             'notPassedFlagged': []
                            }];

                // Check that all capabilities are shown by default.
                expect(ctrl.isCapabilityShown(caps[0])).toEqual(true);
                expect(ctrl.isCapabilityShown(caps[1])).toEqual(true);

                // Check that only capabilities with passed tests are shown.
                ctrl.testStatus = 'passed';
                expect(ctrl.isCapabilityShown(caps[0])).toEqual(true);
                expect(ctrl.isCapabilityShown(caps[1])).toEqual(false);

                // Check that only capabilities with passed tests are shown.
                ctrl.testStatus = 'not passed';
                expect(ctrl.isCapabilityShown(caps[0])).toEqual(false);
                expect(ctrl.isCapabilityShown(caps[1])).toEqual(true);

                // Check that only capabilities with flagged tests are shown.
                ctrl.testStatus = 'flagged';
                expect(ctrl.isCapabilityShown(caps[0])).toEqual(true);
                expect(ctrl.isCapabilityShown(caps[1])).toEqual(false);
            });

        it('should have a method to determine whether a test should be shown',
            function () {
                var cap = {'id': 'cap_id_1',
                           'passedTests': ['test_id_1'],
                           'notPassedTests': [],
                           'passedFlagged': ['test_id_1'],
                           'notPassedFlagged': []
                          };

                expect(ctrl.isTestShown('test_id_1', cap)).toEqual(true);
                ctrl.testStatus = 'passed';
                expect(ctrl.isTestShown('test_id_1', cap)).toEqual(true);
                ctrl.testStatus = 'not passed';
                expect(ctrl.isTestShown('test_id_1', cap)).toEqual(false);
                ctrl.testStatus = 'flagged';
                expect(ctrl.isTestShown('test_id_1', cap)).toEqual(true);
            });

        it('should have a method to determine how many tests in a ' +
           'capability belong under the current test filter',
            function () {
                var cap = {'id': 'cap_id_1',
                           'passedTests': ['t1', 't2', 't3'],
                           'notPassedTests': ['t4', 't5', 't6', 't7'],
                           'passedFlagged': ['t1'],
                           'notPassedFlagged': ['t3', 't4']
                          };

                // Should return the count of all tests.
                expect(ctrl.getCapabilityTestCount(cap)).toEqual(7);

                // Should return the count of passed tests.
                ctrl.testStatus = 'passed';
                expect(ctrl.getCapabilityTestCount(cap)).toEqual(3);

                // Should return the count of failed tests.
                ctrl.testStatus = 'not passed';
                expect(ctrl.getCapabilityTestCount(cap)).toEqual(4);

                // Should return the count of flagged tests.
                ctrl.testStatus = 'flagged';
                expect(ctrl.getCapabilityTestCount(cap)).toEqual(3);
            });

        it('should have a method to determine how many tests in a status ' +
           'belong under the current test filter',
            function () {
                ctrl.caps = {'required': {'caps': [], 'count': 10,
                              'passedCount': 6, 'flagFailCount': 3,
                              'flagPassCount': 2}};

                // Should return the count of all tests (count).
                expect(ctrl.getStatusTestCount('required')).toEqual(10);

                // Should return the count of passed tests (passedCount).
                ctrl.testStatus = 'passed';
                expect(ctrl.getStatusTestCount('required')).toEqual(6);

                // Should return the count of failed tests
                // (count - passedCount).
                ctrl.testStatus = 'not passed';
                expect(ctrl.getStatusTestCount('required')).toEqual(4);

                // Should return the count of flagged tests
                // (flagFailCount + flagPassCount).
                ctrl.testStatus = 'flagged';
                expect(ctrl.getStatusTestCount('required')).toEqual(5);

                // Test when caps has not been set yet.
                ctrl.caps = null;
                expect(ctrl.getStatusTestCount('required')).toEqual(-1);
            });

        it('should have a method to open a modal for the full passed test list',
            function () {
                var modal;
                inject(function ($modal) {
                    modal = $modal;
                });
                spyOn(modal, 'open');
                ctrl.openFullTestListModal();
                expect(modal.open).toHaveBeenCalled();
            });
    });

    describe('FullTestListModalController', function () {
        var modalInstance, ctrl;

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            ctrl = $controller('FullTestListModalController',
                {$modalInstance: modalInstance, tests: ['t1', 't2']}
            );
        }));

        it('should set a scope variable to the passed in tests', function () {
            expect(ctrl.tests).toEqual(['t1', 't2']);
        });

        it('should have a method to close the modal',
            function () {
                ctrl.close();
                expect(modalInstance.dismiss).toHaveBeenCalledWith('exit');
            });

        it('should have a method to convert the tests to a string',
            function () {
                ctrl.tests = ['t2', 't1', 't3'];
                var expectedString = 't1\nt2\nt3';
                expect(ctrl.getTestListString()).toEqual(expectedString);
            });
    });

    describe('TestRaiseAlertModalController', function() {
        var data, modalInstance, ctrl;

        data = {
            mode: 'success',
            title: '',
            text: 'operation successful'
        };

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss'),
                close: jasmine.createSpy('modalInstance.close')
            };
            ctrl = $controller('RaiseAlertModalController',
                {$modalInstance: modalInstance, data: data}
            );
        }));

        it('should close',
            function () {
                ctrl.close();
                expect(modalInstance.close).toHaveBeenCalledWith();
            });
    });

    describe('AuthFailureController', function() {
        var $location, ctrl;

        beforeEach(inject(function ($controller, _$location_) {
            $location = _$location_;
            $location.url('/auth_failure?message=some_error_message');
            ctrl = $controller('AuthFailureController', {});
        }));

        it('should set the authentication failure url based on error message',
            function () {
                expect($location.url()).toBe('/auth_failure?message=' +
                'some_error_message');
                expect(ctrl.message).toBe('some_error_message');
            });
    });
});
