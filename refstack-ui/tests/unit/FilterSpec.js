
/* Jasmine specs for Refstack filters */
describe('Refstack filters', function () {
    'use strict';

    describe('Filter: arrayConverter', function () {
        var $filter;
        beforeEach(module('refstackApp'));
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
});
