/** Jasmine specs for Refstack filters */
describe('Refstack filters', function () {
    'use strict';

    var fakeApiUrl = 'http://foo.bar/v1';
    beforeEach(function () {
        module(function ($provide) {
            $provide.constant('refstackApiUrl', fakeApiUrl);
        });
        module('refstackApp');
    });

    describe('Filter: arrayConverter', function () {
        var $filter;
        beforeEach(inject(function (_$filter_) {
            $filter = _$filter_('arrayConverter');
        }));

        it('should convert dict to array of dict values', function () {
            var object = {'id1': {'key1': 'value1'}, 'id2': {'key2': 'value2'}};
            var expected = [{'key1': 'value1', 'id': 'id1'},
                {'key2': 'value2', 'id': 'id2'}];
            expect($filter(object)).toEqual(expected);
        });
    });

    describe('Filter: capitalize', function() {
        var $filter;
        beforeEach(inject(function(_$filter_) {
            $filter = _$filter_('capitalize');
        }));

        it('should capitalize the first letter', function () {
            var string1 = 'somestring';
            var string2 = 'someString';
            var string3 = 'SOMESTRING';
            expect($filter(string1)).toEqual('Somestring');
            expect($filter(string2)).toEqual('SomeString');
            expect($filter(string3)).toEqual(string3);
        });
    });
});
