//
//   Licensed under the Apache License, Version 2.0 (the "License"); you may
//   not use this file except in compliance with the License. You may obtain
//   a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
//   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
//   License for the specific language governing permissions and limitations
//   under the License.

/*global $:false */
/*global Mustache:false */
/*global window:false */
/*jslint devel: true*/
/* jshint -W097 */
/*jslint node: true */

'use strict';

// Format time (numbers of seconds) in format xx h xx m xx s
// with_sign flag forces to add sign to result
var pretty_time_format = function (time_in, with_sign) {
    var time = Math.abs(time_in),
        hours = Math.floor(time / 3600),
        minutes = Math.floor((time - (hours * 3600)) / 60),
        seconds = time - (hours * 3600) - (minutes * 60),
        result;

    if (hours < 10) {hours = '0' + hours; }
    if (minutes < 10) {minutes = '0' + minutes; }
    if (seconds < 10) {seconds = '0' + seconds; }
    result = minutes + 'm ' + seconds + 's';
    if (hours > 0) {
        return hours + 'h ' + result;
    }
    if (with_sign) {
        if (time_in >= 0) {
            result = '+ ' + result;
        } else {
            result = '- ' + result;
        }
    }
    return result;
};

// Used in templates for rendering custom bullets in capabilities support list
var caps_support = function (text, render) {
    if (this.fully_supported) {
        return render('<span class="fa fa-check cap-passed" title="Fully supported"></span>');
    }
    if (this.partial_supported) {
        return render('<span class="fa fa-question-circle cap-part-passed" title="Partial supported"></span>');
    }
    return render('<span class="fa fa-times cap-failed" title="Unsupported"></span>');
};

// Building data for rendering report for a single test run
// Requires capabilities list. It can be build by "build_caps_list" function
var build_report = function (caps_list, test_result) {
    var other_tests = test_result.results.slice(0),
        result = {
            'only_core': $.cookie('only_core_flag') === 'true',
            'all': $.cookie('admin_filter_flag') === 'all',
            'admin': $.cookie('admin_filter_flag') === 'admin',
            'noadmin': $.cookie('admin_filter_flag') === 'noadmin',
            'cpid': test_result.cpid,
            'duration_seconds': pretty_time_format(test_result.duration_seconds),
            'defcore_tests': {
                capabilities: caps_list.capabilities,
                list: test_result.results.filter(function (test) {
                    return caps_list.global_test_list.indexOf(test) >= 0;
                }),
                passed_tests: test_result.results.filter(function (test) {
                    return caps_list.scope_tests_list.indexOf(test) >= 0;
                }),
                failed_tests: caps_list.scope_tests_list.filter(function (test) {
                    return test_result.results.indexOf(test) < 0;
                }),
                scope_tests_count: caps_list.scope_tests_count
            }
        };
    result.defcore_tests.count = result.defcore_tests.list.length;
    result.defcore_tests.capabilities = caps_list.capabilities.map(function (capability_class) {
        var ext_capability_class = {
            class: capability_class.class,
            count: capability_class.count,
            items : capability_class.items.map(function (capability) {
                return {
                    class: capability.class,
                    description: capability.description,
                    id: capability.id,
                    name: capability.name,
                    tests: capability.tests,
                    tests_count: capability.tests_count
                };
            })

        };
        ext_capability_class.full_support_count = 0;
        ext_capability_class.partial_support_count = 0;
        ext_capability_class.items = ext_capability_class.items.map(function (capability) {
            capability.passed_tests = [];
            capability.failed_tests = [];
            capability.test_chart = [];
            capability.fully_supported = true;
            capability.partial_supported = false;
            capability.tests.forEach(function (test) {
                var passed = test_result.results.indexOf(test) >= 0,
                    test_index = other_tests.indexOf(test);
                if (passed) {
                    capability.partial_supported = true;
                    capability.passed_tests.push(test);
                    if (test_index >= 0) {
                        other_tests.splice(test_index, 1);
                    }
                } else {
                    capability.fully_supported = false;
                    capability.failed_tests.push(test);

                }
            });
            capability.passed_count = capability.passed_tests.length;
            capability.failed_count = capability.failed_tests.length;
            if (capability.fully_supported) {
                capability.partial_supported = false;
            }
            capability.caps_support = function () {return caps_support; };
            if (capability.fully_supported) {
                ext_capability_class.full_support_count += 1;
            }
            if (capability.partial_supported) {
                ext_capability_class.partial_support_count += 1;
            }
            return capability;
        });
        ext_capability_class.items.sort(function (a, b) {
            var ai = 0,
                bi = 0;
            if (a.fully_supported) {ai = 0; } else if (a.partial_supported) {ai = 1; } else {ai = 2; }
            if (b.fully_supported) {bi = 0; } else if (b.partial_supported) {bi = 1; } else {bi = 2; }
            return ((ai > bi) ? -1 : ((ai < bi) ? 1 : 0));
        });
        ext_capability_class.full_unsupport_count = ext_capability_class.count - (ext_capability_class.partial_support_count + ext_capability_class.full_support_count);
        return ext_capability_class;
    });
    result.defcore_tests.total_passed_count = result.defcore_tests.passed_tests.length;
    result.defcore_tests.total_failed_count = result.defcore_tests.failed_tests.length;
    result.other_tests =  {
        'list': other_tests,
        'count': other_tests.length
    };
    return result;
};

// Building data for rendering report for comparison  two test runs.
// Requires capabilities list. It can be build by "build_caps_list" function
var build_diff_report = function (caps_list, test_result, prev_test_result) {
    var diff_report = build_report(caps_list, test_result),
        other_tests = prev_test_result.results.slice(0);
    diff_report.current_run = test_result;
    diff_report.previous_run = prev_test_result;
    diff_report.time_diff = pretty_time_format(diff_report.current_run.duration_seconds - diff_report.previous_run.duration_seconds, true);
    diff_report.current_run.duration_seconds = pretty_time_format(diff_report.current_run.duration_seconds);
    diff_report.previous_run.duration_seconds = pretty_time_format(diff_report.previous_run.duration_seconds);
    diff_report.same_clouds = diff_report.current_run.cpid === diff_report.previous_run.cpid;
    diff_report.defcore_tests.fixed_tests = [];
    diff_report.defcore_tests.broken_tests = [];
    diff_report.defcore_tests.capabilities = diff_report.defcore_tests.capabilities.map(function (capability_class) {
        capability_class.items = capability_class.items.map(function (capability) {
            capability.fixed_tests = [];
            capability.broken_tests = [];
            capability.tests.forEach(function (test) {
                var passed = prev_test_result.results.indexOf(test) >= 0,
                    test_index = other_tests.indexOf(test),
                    failed_index = 0,
                    passed_index = 0;
                if (passed) {
                    if (capability.passed_tests.indexOf(test) < 0) {
                        capability.broken_tests.push(test);
                        if (diff_report.defcore_tests.broken_tests.indexOf(test) < 0) {
                            diff_report.defcore_tests.broken_tests.push(test);
                        }
                        failed_index = capability.failed_tests.indexOf(test);
                        if (failed_index < 0) {
                            alert('Comparison is incorrect!');
                            throw new Error('Comparison is incorrect!');
                        }
                        capability.failed_tests.splice(failed_index, 1);
                    }
                    if (test_index >= 0) {
                        other_tests.splice(test_index, 1);
                    }
                } else {
                    if (capability.failed_tests.indexOf(test) < 0) {
                        capability.fixed_tests.push(test);
                        if (diff_report.defcore_tests.fixed_tests.indexOf(test) < 0) {
                            diff_report.defcore_tests.fixed_tests.push(test);
                        }
                        passed_index = capability.passed_tests.indexOf(test);
                        if (passed_index < 0) {
                            alert('Comparison is incorrect!');
                            throw new Error('Comparison is incorrect!');
                        }
                        capability.passed_tests.splice(passed_index, 1);
                    }
                }
            });
            capability.broken_count = capability.broken_tests.length;
            capability.fixed_count = capability.fixed_tests.length;
            return capability;
        });
        return capability_class;
    });
    diff_report.defcore_tests.passed_tests = diff_report.defcore_tests.passed_tests.filter(function (test) {
        return diff_report.defcore_tests.fixed_tests.indexOf(test) < 0;
    });
    diff_report.defcore_tests.failed_tests = diff_report.defcore_tests.failed_tests.filter(function (test) {
        return diff_report.defcore_tests.broken_tests.indexOf(test) < 0;
    });
    diff_report.defcore_tests.total_failed_count = diff_report.defcore_tests.failed_tests.length;
    diff_report.defcore_tests.total_passed_count = diff_report.defcore_tests.passed_tests.length;
    diff_report.defcore_tests.total_fixed_count = diff_report.defcore_tests.fixed_tests.length;
    diff_report.defcore_tests.total_broken_count = diff_report.defcore_tests.broken_tests.length;
    return diff_report;
};

// Updating admin filter value and render page
var admin_filter_update = function (item) {
    $.cookie('admin_filter_flag', item.name);
    window.render_page();
};

// Updating core filter value and render page
var core_filter_update = function (item) {
    $.cookie('only_core_flag', item.name === 'true');
    window.render_page();
};

// Get filter values (admin and core)
var get_filters_cookie = function () {
    if ($('input#only_core').length === 0) {
        if (!$.cookie('only_core_flag')) {$.cookie('only_core_flag', 'true'); }
    }
    if ($('div#admin_filter').length === 0) {
        if (!$.cookie('admin_filter_flag')) {$.cookie('admin_filter_flag', 'all'); }
    }
    return {only_core: $.cookie('only_core_flag') === 'true', admin_filter: $.cookie('admin_filter_flag')};
};

// Init page spinner
var loading_spin = function () {
    var opts = { lines: 17, length: 40, width: 11, radius: 32, corners: 1,
        rotate: 0, direction: 1, color: '#000', speed: 1, trail: 33,
        shadow: false, hwaccel: false, className: 'spinner', zIndex: 2e9,
        top: '50%', left: '50%' },
        target = document.getElementById('test_results');
    new Spinner(opts).spin(target);
};

// Page post processing for jquery stuff
var post_processing = function post_processing() {
    $('div.cap_shot:odd').addClass('zebra_odd');
    $('div.cap_shot:even').addClass('zebra_even');
    $('div#core_filter').buttonset();
    $('div#admin_filter').buttonset();
    $('#schema_selector').selectmenu({change: function () {window.render_page(); } });

};

// Render page for report from single test run
var render_defcore_report_page = function () {
    var filters = get_filters_cookie(),
        schema = '',
        schema_selector = $('select#schema_selector');

    if (window.result_source === '{{result_source}}') {
        window.result_source = 'sample_test_result.json';
    }
    if (schema_selector.length === 0) {
        schema = 'havanacore.json';
    } else {
        schema = schema_selector[0].value;
    }
    console.log(schema);
    $.when(
        $.get('mustache/report_base.mst', undefined, undefined, 'html'),
        $.get('mustache/single_header.mst', undefined, undefined, 'html'),
        $.get('mustache/single_capabilities_details.mst', undefined, undefined, 'html'),
        $.get('capabilities/' + schema, undefined, undefined, 'json'),
        $.get(window.result_source, undefined, undefined, 'json')
    ).done(function (base_template, header_template, caps_template, schema, test_result) {
        var caps_list = window.build_caps_list(schema[0], filters),
            report = build_report(caps_list, test_result[0]);
        $("div#test_results").html(Mustache.render(base_template[0], report, {
            header: header_template[0],
            caps_details: caps_template[0]
        }));
        post_processing();
    });
};

// Render page for report for comparison two test run
var render_defcore_diff_report_page = function () {
    var filters = get_filters_cookie(),
        schema = '',
        schema_selector = $('select#schema_selector');

    if (window.result_source === '{{result_source}}') {
        window.result_source = 'sample_test_result.json';
    }
    if (window.prev_result_source === '{{prev_result_source}}') {
        window.prev_result_source = 'other_test_result.json';
    }
    if (schema_selector.length === 0) {
        schema = 'havanacore.json';
    } else {
        schema = schema_selector[0].value;
    }
    $.when(
        $.get('mustache/report_base.mst', undefined, undefined, 'html'),
        $.get('mustache/diff_header.mst', undefined, undefined, 'html'),
        $.get('mustache/diff_capabilities_details.mst', undefined, undefined, 'html'),
        $.get('capabilities/' + schema, undefined, undefined, 'json'),
        $.get(window.result_source, undefined, undefined, 'json'),
        $.get(window.prev_result_source, undefined, undefined, 'json')
    ).done(function (base_template, header_template, caps_template, schema,
                     test_result, prev_result) {
        var caps_list = window.build_caps_list(schema[0], filters),
            diff_report = build_diff_report(caps_list, test_result[0], prev_result[0]);
        $("div#test_results").html(Mustache.render(base_template[0], diff_report, {
            header: header_template[0],
            caps_details: caps_template[0]
        }));
        post_processing();
    });
};