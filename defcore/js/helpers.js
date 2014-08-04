function has_upper_case(str) {
    return (/[A-Z]/.test(str));
}

function capitaliseFirstLetter(string){
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function code_url(text, render){
    return render( '<a href="javascript:void(get_code_url(\'' +
            text + '\'));"> [github] </a>' );
}

function get_code_url (test_id) {
    var id = test_id.split('/').join('.');
    var parts = id.split('.');
    var path_array = [];
    for (var i in parts){
        if (has_upper_case(parts[i])) { break }
        path_array.push(parts[i])
    }
    path_array.pop();
    var path = path_array.join('/');
    var test = parts.slice(-1)[0] + '(';
    test = test.replace(/\s+/g, '');
    path = path.replace(/\s+/g, '');
    var url = 'https://api.github.com/search/code?q=' + test +
            ' repo:openstack/tempest extension:py path:' + path;
    console.log(url);
    $.when($.ajax({type: 'GET', url: url, dataType: 'json'})).done(
            function (data, status, xhr) {
                if (data['items'].length < 1) {
                    alert('No test found !')
                }
                var html_url = data['items'][0]['html_url'];
                console.log(data['items'][0]['git_url']);
                $.when($.ajax({type: 'GET', url: data['items'][0]['git_url'], dataType: 'json'})).done(
                        function (data, status, xhr) {
                            var content = window.atob(data['content'].replace(/\s+/g, '')).split('\n');
                            for (var i in content) {
                                if (content[i].indexOf(test) > -1) {
                                    var line = parseInt(i) + 1;
                                    var url = html_url + '#L' + line;
                                    var win = window.open(url, '_blank');
                                    win.focus();
                                }
                            }
                        }
                )
            });

}
function render_header(data){
    var template = $('#header_template').html();
    data["release"] = capitaliseFirstLetter(data["release"]);
    var rendered = Mustache.render(template, data);
    $("div#header").html(rendered);
}

function render_caps(only_core, admin_filter, data){
    var template = $('#capabilities_template').html();
    var criteria_count = Object.keys(data['criteria']).length;
    var caps_dict = {'capabilities': {}};
    var capabilities_count = 0;
    for(var id in data['capabilities']){
        var capability = data['capabilities'][id];
        capability['class'] = id.split('-')[0];
        capability['id'] = id;
        if (!(capability['class'] in caps_dict['capabilities'])){
             caps_dict['capabilities'][capability['class']] = {
                 'items': [],
                 'total': 0
             }
        }
        caps_dict['capabilities'][capability['class']]['total'] += 1;
        if (only_core == true && (capability['core'] !== true)) {continue}
        if (admin_filter == 'Tests require admin rights' && (capability['admin'] !== true)) {continue}
        if (admin_filter == "Tests don't require admin rights" && (capability['admin'] == true)) {continue}
        capability['code_url'] = function(){
            return code_url
        };
        capability['achievements_count'] = capability['achievements'].length;
        capability['tests_count'] = capability['tests'].length;
        caps_dict['capabilities'][capability['class']]['items'].push(capability)
    }
    var caps_list={
        'capabilities': [],
        'criteria_count': criteria_count
    };
    for (var cls in caps_dict['capabilities']){
        if (caps_dict['capabilities'][cls]['items'].length == 0) {
            continue
        }
        caps_list['capabilities'].push({
            'class': cls,
            'items': caps_dict['capabilities'][cls]['items'],
            'count': caps_dict['capabilities'][cls]['items'].length,
            'total': caps_dict['capabilities'][cls]['total']
        })
    }
    var rendered = Mustache.render(template, caps_list);

    $("div#capabilities").html(rendered);
}

function render_criteria(data){
    var template = $('#criteria_template').html();
    var crits = {'criteria': []};
    for(var tag in data['criteria']){
        var criterion = data['criteria'][tag];
        criterion['tag'] = tag;
        crits['criteria'].push(criterion);
        }
    var rendered = Mustache.render(template, crits);

    $("ul#criteria").html(rendered);
}

function create_caps() {

    if (document.getElementById('only_core')){
        only_core = document.getElementById('only_core').checked
    }
    else only_core = true;
    if (document.getElementById('admin')){
        admin_filter = document.getElementById('admin').value
    }
    else admin_filter = 'All tests';
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: 'havanacore.json',
        success: function(data, status, xhr) {
            render_caps(only_core, admin_filter, data);
            render_criteria(data);
            render_header(data)
        }
    });
}
window.onload = create_caps();
