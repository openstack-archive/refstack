describe('Auth', function () {
    'use strict';

    var fakeApiUrl = 'http://foo.bar/v1';
    var $window, $rootScope, $httpBackend;
    beforeEach(function () {
        $window = {location: { href: jasmine.createSpy()} };
        module(function ($provide) {
            $provide.constant('refstackApiUrl', fakeApiUrl);
            $provide.value('$window', $window);
        });
        module('refstackApp');
        inject(function (_$httpBackend_, _$rootScope_) {
            $httpBackend = _$httpBackend_;
            $rootScope = _$rootScope_;
        });
        $httpBackend.whenGET('/components/home/home.html')
            .respond('<div>mock template</div>');
    });
    it('should show signin url for signed user', function () {
        $httpBackend.expectGET(fakeApiUrl +
            '/profile').respond({'openid': 'foo@bar.com',
            'email': 'foo@bar.com',
            'fullname': 'foo' });
        $httpBackend.flush();
        $rootScope.auth.doSignIn();
        expect($window.location.href).toBe(fakeApiUrl + '/auth/signin');
        expect($rootScope.auth.isAuthenticated).toBe(true);
    });

    it('should show signout url for not signed user', function () {
        $httpBackend.expectGET(fakeApiUrl +
            '/profile').respond(401);
        $httpBackend.flush();
        $rootScope.auth.doSignOut();
        expect($window.location.href).toBe(fakeApiUrl + '/auth/signout');
        expect($rootScope.auth.isAuthenticated).toBe(false);
    });
});
