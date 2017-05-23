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

    describe('AboutController', function () {
        var $location, ctrl;

        beforeEach(inject(function ($controller, _$location_) {
            $location = _$location_;
            ctrl = $controller('AboutController', {});
            ctrl.options = {
                'about' : {
                    'title': 'About RefStack',
                    'template': 'about-template'
                },
                'option1' : {
                    'title': 'Option One',
                    'template': 'template-1'
                }
            };
        }));

        it('should have a function to select an option',
            function () {
                ctrl.selectOption('option1');
                expect(ctrl.selected).toBe('option1');
                expect(ctrl.template).toBe('template-1');
                expect($location.hash()).toBe('option1');
            });

        it('should have a function to get the URL hash and select it',
            function () {
                // Test existing option.
                $location.url('/about#option1');
                ctrl.getHash();
                expect(ctrl.selected).toBe('option1');
                expect(ctrl.template).toBe('template-1');

                // Test nonexistent option.
                $location.url('/about#foobar');
                ctrl.getHash();
                expect(ctrl.selected).toBe('about');
                expect(ctrl.template).toBe('about-template');
            });

    });

    describe('GuidelinesController', function () {
        var ctrl;

        beforeEach(inject(function ($controller) {
            ctrl = $controller('GuidelinesController', {});
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
                '/guidelines').respond(['next.json', '2015.03.json',
                                        '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/guidelines/2015.04.json').respond(fakeCaps);
                $httpBackend.flush();
                // The version list should be sorted latest first.
                expect(ctrl.versionList).toEqual(['next.json',
                                                  '2015.04.json',
                                                  '2015.03.json']);
                expect(ctrl.guidelines).toEqual(fakeCaps);
                // The guideline status should be approved.
                expect(ctrl.guidelines.status).toEqual('approved');
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

        it('should have a method to open a modal for the relevant test list',
            function () {
                var modal;
                inject(function ($uibModal) {
                    modal = $uibModal;
                });
                spyOn(modal, 'open');
                ctrl.openTestListModal();
                expect(modal.open).toHaveBeenCalled();
            });
    });

    describe('TestListModalController', function () {
        var modalInstance, ctrl, $window;

        beforeEach(inject(function ($controller, _$window_) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            $window = _$window_;
            ctrl = $controller('TestListModalController',
                {$uibModalInstance: modalInstance,
                 target: 'platform',
                 version: '2016.01',
                 status: {required: true, advisory: false}}
            );
        }));

        it('should have a method to close the modal',
            function () {
                ctrl.close();
                expect(modalInstance.dismiss).toHaveBeenCalledWith('exit');
            });

        it('should have a method to download the test list string',
            function () {
                var fakeResp = 'test1\ntest2\ntest3';
                $httpBackend.expectGET(fakeApiUrl +
                '/guidelines/2016.01/tests?target=platform&' +
                'type=required&alias=true&flag=false').respond(fakeResp);
                $httpBackend.flush();
                ctrl.updateTestListString();
                expect(ctrl.testListCount).toBe(3);
            });
    });

    describe('ResultsController', function () {
        var scope, ctrl;
        var fakeResponse = {
            'pagination': {'current_page': 1, 'total_pages': 2},
            'results': [{
                'created_at': '2015-03-09 01:23:45',
                'id': 'some-id',
                'cpid': 'some-cpid'
            }]
        };
        var fakeVendorResp = {
            'vendors': [{'id': 'fakeid', 'name': 'Foo Vendor'}]
        };

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            ctrl = $controller('ResultsController', {$scope: scope});
            $httpBackend.when('GET', fakeApiUrl +
                '/results?page=1').respond(fakeResponse);
            $httpBackend.when('GET', fakeApiUrl +
                '/vendors').respond(fakeVendorResp);
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

        it('should have a function to associate metadata to a test run',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/results?page=1')
                    .respond(fakeResponse);
                ctrl.data = fakeResponse;
                ctrl.data.results[0].targetEdit = true;
                ctrl.associateMeta(0, 'target', 'platform');
                $httpBackend.expectPOST(
                    fakeApiUrl + '/results/some-id/meta/target',
                    'platform')
                    .respond(201, '');
                $httpBackend.flush();
                expect(ctrl.data.results[0].targetEdit).toBe(false);
            });

        it('should have a function to delete metadata from a test run',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/results?page=1')
                    .respond(fakeResponse);
                ctrl.data = fakeResponse;
                ctrl.data.results[0].targetEdit = true;
                ctrl.associateMeta(0, 'target', '');
                $httpBackend.expectDELETE(
                    fakeApiUrl + '/results/some-id/meta/target')
                    .respond(200, '');
                $httpBackend.flush();
                expect(ctrl.data.results[0].targetEdit).toBe(false);
            });

        it('should have a function to get guideline versions',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/results?page=1')
                    .respond(fakeResponse);
                $httpBackend.expectGET(fakeApiUrl +
                    '/guidelines').respond(['2015.03.json', '2015.04.json']);
                ctrl.getVersionList();
                $httpBackend.flush();
                // Expect the list to have the latest guideline first.
                expect(ctrl.versionList).toEqual(['2015.04.json',
                                                  '2015.03.json']);
            });

        it('should have a function to get products manageable by a user',
            function () {
                var prodResp = {'products': [{'id': 'abc',
                                              'can_manage': true},
                                             {'id': 'foo',
                                              'can_manage': false}]};
                ctrl.products = null;
                $httpBackend.expectGET(fakeApiUrl + '/products')
                    .respond(200, prodResp);
                ctrl.getUserProducts();
                $httpBackend.flush();
                var expected = {'abc': {'id': 'abc', 'can_manage': true}};
                expect(ctrl.products).toEqual(expected);
            });

        it('should have a function to get a listing of vendors',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/vendors')
                    .respond(fakeVendorResp);
                ctrl.getVendors();
                $httpBackend.flush();
                var expected = fakeVendorResp.vendors[0];
                expect(ctrl.vendors.fakeid).toEqual(expected);
            });

        it('should have a function to associate a product version to a test',
            function () {
                var result = {'id': 'bar',
                              'selectedVersion': {'id': 'foo'},
                              'selectedProduct': {'id': 'prod'}};
                ctrl.products = null;
                $httpBackend.expectPUT(fakeApiUrl + '/results/bar')
                    .respond(201);
                ctrl.associateProductVersion(result);
                $httpBackend.flush();
                var expected = {'id': 'foo', 'product_info': {'id': 'prod'}};
                expect(result.product_version).toEqual(expected);
            });

        it('should have a function to get product versions',
            function () {
                var result = {'id': 'bar',
                              'selectedProduct': {'id': 'prod'}};
                var verResp = [{'id': 'ver1', 'version': '1.0'},
                               {'id': 'ver2', 'version': null}];
                ctrl.products = null;
                $httpBackend.expectGET(fakeApiUrl + '/products/prod/versions')
                    .respond(200, verResp);
                ctrl.getProductVersions(result);
                $httpBackend.flush();
                expect(result.productVersions).toEqual(verResp);
                var expected = {'id': 'ver2', 'version': null};
                expect(result.selectedVersion).toEqual(expected);
            });
    });

    describe('ResultsReportController', function () {
        var stateparams, ctrl;
        var fakeResultResponse = {'results': ['test_id_1'], 'meta': {
            'public_key': 'ssh-rsa', 'guideline': '2015.04.json', 'target':
            'object'
        }};
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
            $httpBackend.when('GET', fakeApiUrl +
                '/results/1234').respond(fakeResultResponse);
            $httpBackend.when('GET', fakeApiUrl +
                '/guidelines').respond(['2015.03.json', '2015.04.json']);
            $httpBackend.when('GET', fakeApiUrl +
                '/guidelines/2015.04.json').respond(fakeCapabilityResponse);
        }));

        it('should make all necessary API requests to get results ' +
            'and guidelines',
            function () {
                $httpBackend.expectGET(fakeApiUrl +
                '/results/1234').respond(fakeResultResponse);
                $httpBackend.expectGET(fakeApiUrl +
                '/guidelines').respond(['2015.03.json', '2015.04.json']);
                // Should call request with latest version.
                $httpBackend.expectGET(fakeApiUrl +
                '/guidelines/2015.04.json').respond(fakeCapabilityResponse);
                $httpBackend.flush();
                expect(ctrl.resultsData).toEqual(fakeResultResponse);
                // The version list should be sorted latest first.
                expect(ctrl.versionList).toEqual(['2015.04.json',
                                                   '2015.03.json']);
                expect(ctrl.guidelineData).toEqual(fakeCapabilityResponse);
                // The guideline status should be approved.
                expect(ctrl.guidelineData.status).toEqual('approved');
                expect(ctrl.schemaVersion).toEqual('1.2');
            });

        it('should have a method that creates an object containing each ' +
           'relevant capability and its highest priority status',
            function () {
                ctrl.guidelineData = {
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
                ctrl.guidelineData = fakeCapabilityResponse;
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
                ctrl.guidelineData = {
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

                // Test case where a component capability isn't listed in
                // the capabilities object.
                ctrl.guidelineData.components.compute.removed = ['fake_cap'];
                ctrl.buildCapabilitiesObject();
                expectedCapsObject.removed.caps = [{
                    'id': 'fake_cap',
                    'passedTests': [],
                    'notPassedTests': [],
                    'passedFlagged': [],
                    'notPassedFlagged': []
                }];
                expect(ctrl.caps).toEqual(expectedCapsObject);
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
                    'Interop Working Group has flagged this test.');

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

        it('should have a method to update the verification status of a test',
            function () {
                $httpBackend.flush();
                ctrl.isVerified = 1;
                $httpBackend.expectPUT(fakeApiUrl + '/results/1234',
                    {'verification_status': ctrl.isVerified}).respond(204, '');
                $httpBackend.when('GET', /\.html$/).respond(200);
                ctrl.updateVerificationStatus();
                $httpBackend.flush();
                expect(ctrl.resultsData.verification_status).toEqual(1);

            });

        it('should have a method to open a modal for the full passed test list',
            function () {
                var modal;
                inject(function ($uibModal) {
                    modal = $uibModal;
                });
                spyOn(modal, 'open');
                ctrl.openFullTestListModal();
                expect(modal.open).toHaveBeenCalled();
            });

        it('should have a method to open a modal for editing test metadata',
            function () {
                var modal;
                inject(function ($uibModal) {
                    modal = $uibModal;
                });
                spyOn(modal, 'open');
                ctrl.openEditTestModal();
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
                {$uibModalInstance: modalInstance, tests: ['t1', 't2']}
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

    describe('EditTestModalController', function () {
        var modalInstance, ctrl, state;
        var fakeResultsData = {
            'results': ['test_id_1'],
            'id': 'some-id',
            'meta': {
                'public_key': 'ssh-rsa', 'guideline': '2015.04.json',
                'target': 'object'
            }
        };
        var fakeProdResp = {'products': [{'id': 1234}]};
        var fakeVersionResp = [{'id': 'ver1', 'version': '1.0'},
                               {'id': 'ver2', 'version': null}];

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            state = {
                reload: jasmine.createSpy('state.reload')
            };
            ctrl = $controller('EditTestModalController',
                {$uibModalInstance: modalInstance, $state: state,
                 resultsData: fakeResultsData}
            );
            $httpBackend.when('GET', fakeApiUrl +
                '/guidelines').respond(['2015.03.json', '2015.04.json']);
            $httpBackend.when('GET', fakeApiUrl + '/products')
                    .respond(200, fakeResultsData);
            $httpBackend.when('GET', fakeApiUrl +
                '/products/1234/versions').respond(fakeVersionResp);
        }));

        it('should be able to get product versions', function () {
            ctrl.selectedProduct = {'id': '1234'};
            ctrl.products = null;
            $httpBackend.expectGET(fakeApiUrl + '/products/1234/versions')
                .respond(200, fakeVersionResp);
            ctrl.getProductVersions();
            $httpBackend.flush();
            expect(ctrl.productVersions).toEqual(fakeVersionResp);
            var expected = {'id': 'ver2', 'version': null};
            expect(ctrl.selectedVersion).toEqual(expected);
        });

        it('should have a method to save all changes made.', function () {
            ctrl.metaCopy.target = 'platform';
            ctrl.metaCopy.shared = 'true';
            ctrl.selectedVersion = {'id': 'ver2', 'version': null};
            ctrl.saveChanges();
            // Only meta changed should send a POST request.
            $httpBackend.expectPOST(
                fakeApiUrl + '/results/some-id/meta/target',
                'platform')
                .respond(201, '');
            $httpBackend.expectPOST(
                fakeApiUrl + '/results/some-id/meta/shared',
                'true')
                .respond(201, '');
            $httpBackend.expectPUT(fakeApiUrl + '/results/some-id',
                {'product_version_id': 'ver2'})
                .respond(201);
            $httpBackend.flush();
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
                {$uibModalInstance: modalInstance, data: data}
            );
        }));

        it('should close',
            function () {
                ctrl.close();
                expect(modalInstance.close).toHaveBeenCalledWith();
            });
    });

    describe('TestCustomConfirmModalController', function() {
        var data, someFunc, modalInstance, ctrl;

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss'),
                close: jasmine.createSpy('modalInstance.close')
            };

            someFunc = jasmine.createSpy('someFunc');
            data = {
                text: 'Some input',
                successHandler: someFunc
            };

            ctrl = $controller('CustomConfirmModalController',
                {$uibModalInstance: modalInstance, data: data}
            );
        }));

        it('should have a function to confirm',
            function () {
                ctrl.inputText = 'foo';
                ctrl.confirm();
                expect(someFunc).toHaveBeenCalledWith('foo');
            });

        it('should have a function to dismiss the modal',
            function () {
                ctrl.cancel();
                expect(modalInstance.dismiss).toHaveBeenCalledWith('cancel');
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

    describe('VendorController', function() {
        var rootScope, scope, stateParams, ctrl;
        var confirmModal = jasmine.createSpy('confirmModal');
        var fakeResp = {'id': 'fake-id', 'type': 1,
                         'can_manage': true, 'properties' : {}};
        var fakeUsersResp = [{'openid': 'foo'}];
        var fakeProdResp = {'products': [{'id': 123}]};
        var fakeWindow = {
            location: {
                href: ''
            }
        };

        beforeEach(inject(function ($controller, $rootScope) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            rootScope.auth = {'currentUser' : {'is_admin': false,
                                               'openid': 'foo'}
                             };
            stateParams = {vendorID: 1234};
            ctrl = $controller('VendorController',
                {$rootScope: rootScope, $scope: scope,
                 $stateParams: stateParams, $window: fakeWindow,
                 confirmModal: confirmModal}
            );

            $httpBackend.when('GET', fakeApiUrl +
            '/vendors/1234').respond(fakeResp);
            $httpBackend.when('GET', fakeApiUrl +
            '/products?organization_id=1234').respond(fakeProdResp);
            $httpBackend.when('GET', fakeApiUrl +
            '/vendors/1234/users').respond(fakeUsersResp);
        }));

        it('should have a function to get vendor info from API',
            function () {
                ctrl.getVendor();
                $httpBackend.flush();
                expect(ctrl.vendor.id).toEqual('fake-id');
                expect(ctrl.vendor.can_manage).toEqual(true);
                expect(ctrl.vendor.canDelete).toEqual(true);
                expect(ctrl.vendor.canRegister).toEqual(true);
                expect(ctrl.vendor.canApprove).toEqual(false);
            });

        it('should have a function to get vendor users',
            function () {
                ctrl.getVendorUsers();
                $httpBackend.flush();
                expect(ctrl.vendorUsers).toEqual(fakeUsersResp);
                expect(ctrl.currentUser).toEqual('foo');
            });

        it('should have a function to get vendor products',
            function () {
                ctrl.vendorProducts = null;
                ctrl.getVendorProducts();
                $httpBackend.flush();
                expect(ctrl.vendorProducts).toEqual(fakeProdResp.products);
            });

        it('should have a function to register a vendor',
            function () {
                $httpBackend.expectPOST(
                    fakeApiUrl + '/vendors/1234/action',
                    {'register': null})
                    .respond(201, '');
                ctrl.registerVendor();
                $httpBackend.flush();
            });

        it('should have a function to approve a vendor',
            function () {
                $httpBackend.expectPOST(
                    fakeApiUrl + '/vendors/1234/action',
                    {'approve': null})
                    .respond(201, '');
                ctrl.approveVendor();
                $httpBackend.flush();
            });

        it('a confirmation modal should come up when declining a vendor',
            function () {
                ctrl.declineVendor();
                expect(confirmModal).toHaveBeenCalled();
            });

        it('should have a function to delete a vendor',
            function () {
                $httpBackend.expectDELETE(
                    fakeApiUrl + '/vendors/1234').respond(202, '');
                ctrl.deleteVendor();
                $httpBackend.flush();
                expect(fakeWindow.location.href).toEqual('/');
            });

        it('should have to a function to remove a user from a vendor',
            function () {
                var fakeId = 'fake-id';
                $httpBackend.expectDELETE(
                    fakeApiUrl + '/vendors/1234/users/' + btoa(fakeId))
                    .respond(202, '');
                ctrl.removeUserFromVendor(fakeId);
                $httpBackend.flush();
            });

        it('should have to a function to add a user to a vendor',
            function () {
                var fakeId = 'fake-id';
                $httpBackend.expectPUT(
                    fakeApiUrl + '/vendors/1234/users/' + btoa(fakeId))
                    .respond(204, '');
                ctrl.addUserToVendor(fakeId);
                $httpBackend.flush();
            });
    });

    describe('VendorEditModalController', function() {
        var rootScope, ctrl, modalInstance, state;
        var fakeVendor = {'name': 'Foo', 'description': 'Bar', 'id': '1234',
                          'properties': {'key1': 'value1', 'key2': 'value2'}};

        beforeEach(inject(function ($controller, $rootScope) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            state = {
                reload: jasmine.createSpy('state.reload')
            };
            rootScope = $rootScope.$new();
            rootScope.auth = {'currentUser' : {'is_admin': true,
                                               'openid': 'foo'}
                             };
            ctrl = $controller('VendorEditModalController',
                {$rootScope: rootScope,
                 $uibModalInstance: modalInstance, $state: state,
                 vendor: fakeVendor}
            );

        }));

        it('should be able to add/remove properties',
            function () {
                var expected = [{'key': 'key1', 'value': 'value1'},
                                {'key': 'key2', 'value': 'value2'}];
                expect(ctrl.vendorProperties).toEqual(expected);
                ctrl.removeProperty(0);
                expected = [{'key': 'key2', 'value': 'value2'}];
                expect(ctrl.vendorProperties).toEqual(expected);
                ctrl.addField();
                expected = [{'key': 'key2', 'value': 'value2'},
                            {'key': '', 'value': ''}];
                expect(ctrl.vendorProperties).toEqual(expected);
            });

        it('should have a function to save changes',
            function () {
                var expectedContent = {
                    'name': 'Foo1', 'description': 'Bar',
                    'properties': {'key1': 'value1', 'key2': 'value2'}
                };
                $httpBackend.expectPUT(
                    fakeApiUrl + '/vendors/1234', expectedContent)
                    .respond(200, '');
                ctrl.vendor.name = 'Foo1';
                ctrl.saveChanges();
                $httpBackend.flush();
            });

        it('should have a function to exit the modal',
            function () {
                ctrl.close();
                expect(modalInstance.dismiss).toHaveBeenCalledWith('exit');
            });
    });

    describe('VendorsController', function () {
        var rootScope, scope, ctrl;
        var fakeResp = {'vendors': [{'can_manage': true,
                                     'type': 3,
                                     'name': 'Foo'},
                                    {'can_manage': true,
                                     'type': 3,
                                     'name': 'Bar'}]};
        beforeEach(inject(function ($controller, $rootScope) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            rootScope.auth = {'currentUser' : {'is_admin': false,
                                               'openid': 'foo'}
                             };
            ctrl = $controller('VendorsController',
                {$rootScope: rootScope, $scope: scope}
            );
            $httpBackend.when('GET', fakeApiUrl +
                '/vendors').respond(fakeResp);
        }));

        it('should have a function to get a listing of all vendors',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/vendors')
                    .respond(fakeResp);
                ctrl.update();
                $httpBackend.flush();
                expect(ctrl.rawData).toEqual(fakeResp);
            });

        it('should have a function to update/sort data based on settings',
            function () {
                ctrl.rawData = fakeResp;
                ctrl.updateData();
                var expectedResponse = {'vendors': [{'can_manage': true,
                                                     'type': 3,
                                                     'name' : 'Bar'},
                                                    {'can_manage': true,
                                                     'type': 3,
                                                     'name': 'Foo'}]};
                expect(ctrl.data).toEqual(expectedResponse);
            });

        it('should have a function to determine if a vendor should be shown',
            function () {
                var fakeVendor = {'type': 0, 'can_manage': false};
                expect(ctrl._filterVendor(fakeVendor)).toEqual(true);
                ctrl.isUserVendors = true;
                expect(ctrl._filterVendor(fakeVendor)).toEqual(false);
                ctrl.isUserVendors = false;
                rootScope.auth.currentUser.is_admin = true;
                expect(ctrl._filterVendor(fakeVendor)).toEqual(true);
            });

        it('should have a function to add a new vendor',
            function () {
                ctrl.name = 'New Vendor';
                ctrl.description = 'A description';
                $httpBackend.expectPOST(
                    fakeApiUrl + '/vendors',
                    {name: ctrl.name, description: ctrl.description})
                    .respond(200, fakeResp);
                ctrl.addVendor();
                $httpBackend.flush();
            });
    });

    describe('ProductsController', function() {
        var rootScope, scope, ctrl;
        var vendResp = {'vendors': [{'can_manage': true,
                                     'type': 3,
                                     'name': 'Foo',
                                     'id': '123'}]};
        var prodResp = {'products': [{'id': 'abc',
                                      'product_type': 1,
                                      'public': 1,
                                      'name': 'Foo Product',
                                      'organization_id': '123'}]};

        beforeEach(inject(function ($controller, $rootScope) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            rootScope.auth = {'currentUser' : {'is_admin': false,
                                               'openid': 'foo'}
                             };
            ctrl = $controller('ProductsController',
                {$rootScope: rootScope, $scope: scope}
            );
            $httpBackend.when('GET', fakeApiUrl +
                '/vendors').respond(vendResp);
            $httpBackend.when('GET', fakeApiUrl +
                '/products').respond(prodResp);
        }));

        it('should have a function to get/update vendors',
            function () {
                $httpBackend.flush();
                var newVendResp = {'vendors': [{'name': 'Foo',
                                                'id': '123',
                                                'can_manage': true},
                                               {'name': 'Bar',
                                                'id': '345',
                                                'can_manage': false}]};
                $httpBackend.expectGET(fakeApiUrl + '/vendors')
                    .respond(200, newVendResp);
                ctrl.updateVendors();
                $httpBackend.flush();
                expect(ctrl.allVendors).toEqual({'123': {'name': 'Foo',
                                                         'id': '123',
                                                         'can_manage': true},
                                                 '345': {'name': 'Bar',
                                                         'id': '345',
                                                         'can_manage': false}});
                expect(ctrl.vendors).toEqual([{'name': 'Foo',
                                               'id': '123',
                                               'can_manage': true}]);
            });

        it('should have a function to get products',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/products')
                    .respond(200, prodResp);
                ctrl.update();
                $httpBackend.flush();
                expect(ctrl.rawData).toEqual(prodResp);
            });

        it('should have a function to update the view',
            function () {
                $httpBackend.flush();
                ctrl.allVendors = {'123': {'name': 'Foo',
                                           'id': '123',
                                           'can_manage': true}};
                ctrl.updateData();
                var expectedData = {'products': [{'id': 'abc',
                                                  'product_type': 1,
                                                  'public': 1,
                                                  'name': 'Foo Product',
                                                  'organization_id': '123'}]};
                expect(ctrl.data).toEqual(expectedData);
            });

        it('should have a function to map product types with descriptions',
            function () {
                expect(ctrl.getProductTypeDescription(0)).toEqual('Distro');
                expect(ctrl.getProductTypeDescription(1))
                    .toEqual('Public Cloud');
                expect(ctrl.getProductTypeDescription(2))
                    .toEqual('Hosted Private Cloud');
                expect(ctrl.getProductTypeDescription(5)).toEqual('Unknown');
            });
    });

    describe('ProductController', function() {
        var rootScope, scope, stateParams, ctrl;
        var fakeProdResp = {'product_type': 1,
                            'product_ref_id': null,
                            'name': 'Good Stuff',
                            'created_at': '2016-01-01 01:02:03',
                            'updated_at': '2016-06-15 01:02:04',
                            'properties': null,
                            'organization_id': 'fake-org-id',
                            'public': true,
                            'can_manage': true,
                            'created_by_user': 'fake-open-id',
                            'type': 0,
                            'id': '1234',
                            'description': 'some description'};
        var fakeVersionResp = [{'id': 'asdf',
                               'cpid': null,
                               'version': '1.0',
                               'product_id': '1234'}];
        var fakeTestsResp = {'pagination': {'current_page': 1,
                                            'total_pages': 1},
                             'results':[{'id': 'foo-test'}]};
        var fakeVendorResp = {'id': 'fake-org-id',
                              'type': 3,
                              'can_manage': true,
                              'properties' : {},
                              'name': 'Foo Vendor',
                              'description': 'foo bar'};
        var fakeWindow = {
            location: {
                href: ''
            }
        };

        beforeEach(inject(function ($controller, $rootScope) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            stateParams = {id: 1234};
            rootScope.auth = {'currentUser' : {'is_admin': false,
                                               'openid': 'foo'}
                             };
            ctrl = $controller('ProductController',
                {$rootScope: rootScope, $scope: scope,
                 $stateParams: stateParams, $window: fakeWindow}
            );
            $httpBackend.when('GET', fakeApiUrl +
                '/products/1234').respond(fakeProdResp);
            $httpBackend.when('GET', fakeApiUrl +
                '/products/1234/versions').respond(fakeVersionResp);
            $httpBackend.when('GET', fakeApiUrl +
                '/results?page=1&product_id=1234').respond(fakeTestsResp);
            $httpBackend.when('GET', fakeApiUrl +
                '/vendors/fake-org-id').respond(fakeVendorResp);
        }));

        it('should have a function to get product information',
            function () {
                $httpBackend.expectGET(fakeApiUrl + '/products/1234')
                    .respond(200, fakeProdResp);
                $httpBackend.expectGET(fakeApiUrl + '/vendors/fake-org-id')
                    .respond(200, fakeVendorResp);
                ctrl.getProduct();
                $httpBackend.flush();
                expect(ctrl.product).toEqual(fakeProdResp);
                expect(ctrl.vendor).toEqual(fakeVendorResp);
            });

        it('should have a function to get a list of product versions',
            function () {
                $httpBackend
                    .expectGET(fakeApiUrl + '/products/1234/versions')
                    .respond(200, fakeVersionResp);
                ctrl.getProductVersions();
                $httpBackend.flush();
                expect(ctrl.productVersions).toEqual(fakeVersionResp);
            });

        it('should have a function to delete a product',
            function () {
                $httpBackend.expectDELETE(fakeApiUrl + '/products/1234')
                    .respond(202, '');
                ctrl.deleteProduct();
                $httpBackend.flush();
                expect(fakeWindow.location.href).toEqual('/');
            });

        it('should have a function to delete a product version',
            function () {
                $httpBackend
                    .expectDELETE(fakeApiUrl + '/products/1234/versions/abc')
                    .respond(204, '');
                ctrl.deleteProductVersion('abc');
                $httpBackend.flush();
            });

        it('should have a function to add a product version',
            function () {
                ctrl.newProductVersion = 'abc';
                $httpBackend.expectPOST(
                    fakeApiUrl + '/products/1234/versions',
                    {version: 'abc'})
                    .respond(200, {'id': 'foo'});
                ctrl.addProductVersion();
                $httpBackend.flush();
            });

        it('should have a function to get tests on a product',
            function () {
                ctrl.getProductTests();
                $httpBackend.flush();
                expect(ctrl.testsData).toEqual(fakeTestsResp.results);
                expect(ctrl.currentPage).toEqual(1);
            });

        it('should have a function to unassociate a test from a product',
            function () {
                ctrl.testsData = [{'id': 'foo-test'}];
                $httpBackend.expectPUT(
                    fakeApiUrl + '/results/foo-test',
                    {product_version_id: null})
                    .respond(200, {'id': 'foo-test'});
                ctrl.unassociateTest(0);
                $httpBackend.flush();
                expect(ctrl.testsData).toEqual([]);
            });

        it('should have a function to switch the publicity of a project',
            function () {
                ctrl.product = {'public': true};
                $httpBackend.expectPUT(fakeApiUrl + '/products/1234',
                    {'public': false})
                    .respond(200, fakeProdResp);
                ctrl.switchProductPublicity();
                $httpBackend.flush();
            });

        it('should have a method to open a modal for version management',
            function () {
                var modal;
                inject(function ($uibModal) {
                    modal = $uibModal;
                });
                spyOn(modal, 'open');
                ctrl.openVersionModal();
                expect(modal.open).toHaveBeenCalled();
            });

        it('should have a method to open a modal for product editing',
            function () {
                var modal;
                inject(function ($uibModal) {
                    modal = $uibModal;
                });
                spyOn(modal, 'open');
                ctrl.openProductEditModal();
                expect(modal.open).toHaveBeenCalled();
            });
    });

    describe('ProductVersionModalController', function() {

        var ctrl, modalInstance, state, parent;
        var fakeVersion = {'id': 'asdf', 'cpid': null,
                           'version': '1.0','product_id': '1234'};

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            parent = {
                deleteProductVersion: jasmine.createSpy('deleteProductVersion')
            };
            ctrl = $controller('ProductVersionModalController',
                {$uibModalInstance: modalInstance, $state: state,
                 version: fakeVersion, parent: parent}
            );
        }));

        it('should have a function to prompt a version deletion',
            function () {
                ctrl.deleteProductVersion();
                expect(parent.deleteProductVersion)
                    .toHaveBeenCalledWith('asdf');
                expect(modalInstance.dismiss).toHaveBeenCalledWith('exit');
            });

        it('should have a function to save changes',
            function () {
                ctrl.version.cpid = 'some-cpid';
                var expectedContent = { 'cpid': 'some-cpid'};
                $httpBackend.expectPUT(
                    fakeApiUrl + '/products/1234/versions/asdf',
                    expectedContent).respond(200, '');
                ctrl.saveChanges();
                $httpBackend.flush();
            });
    });

    describe('ProductEditModalController', function() {
        var ctrl, modalInstance, state;
        var fakeProduct = {'name': 'Foo', 'description': 'Bar', 'id': '1234',
                           'properties': {'key1': 'value1'}};
        var fakeVersion = {'version': null, 'product_id': '1234',
                           'cpid': null, 'id': 'asdf'};

        beforeEach(inject(function ($controller) {
            modalInstance = {
                dismiss: jasmine.createSpy('modalInstance.dismiss')
            };
            state = {
                reload: jasmine.createSpy('state.reload')
            };
            ctrl = $controller('ProductEditModalController',
                {$uibModalInstance: modalInstance, $state: state,
                 product: fakeProduct,
                 version: fakeVersion}
            );
        }));

        it('should be able to add/remove properties',
            function () {
                var expected = [{'key': 'key1', 'value': 'value1'}];
                expect(ctrl.productProperties).toEqual(expected);
                ctrl.removeProperty(0);
                expect(ctrl.productProperties).toEqual([]);
                ctrl.addField();
                expected = [{'key': '', 'value': ''}];
                expect(ctrl.productProperties).toEqual(expected);
            });

        it('should have a function to save changes',
            function () {
                var expectedContent = {
                    'name': 'Foo1', 'description': 'Bar',
                    'properties': {'key1': 'value1'}
                };
                var verContent = {'cpid': 'abc'};
                $httpBackend.expectPUT(
                    fakeApiUrl + '/products/1234', expectedContent)
                    .respond(200, '');
                $httpBackend.expectPUT(
                    fakeApiUrl + '/products/1234/versions/asdf', verContent)
                    .respond(200, '');
                ctrl.productVersion.cpid = 'abc';
                ctrl.product.name = 'Foo1';
                ctrl.saveChanges();
                $httpBackend.flush();
            });

        it('should have a function to exit the modal',
            function () {
                ctrl.close();
                expect(modalInstance.dismiss).toHaveBeenCalledWith('exit');
            });
    });
});
