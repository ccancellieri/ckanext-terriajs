export const initialize = () => {
    window.JSONEditor.defaults.callbacks = {
        // "button":  function view_info(jseditor_editor, input){
        //         console.log(input);
        // },
        "autocomplete": {
        // This is callback functions for the "autocomplete" editor
        // In the schema you refer to the callback function by key
        // Note: 1st parameter in callback is ALWAYS a reference to the current editor.
        // So you need to add a variable to the callback to hold this (like the
        // "jseditor_editor" variable in the examples below.)

        // Setup API calls
            "view_search": function search(jseditor_editor, input) {
                var url = new URL('terriajs/search?'+
                        'resource_name='+ encodeURI(input)+
                        '&dataset_title='+ encodeURI(input)+
                        '&dataset_description='+ encodeURI(input),jsonschema.ckanUrl);
                if (input.length < 2) {
                    return [];
                }
                return fetch(url).then(function (request) {
                        if (request.status === 200) {
                            return request.json();
                        } else {
                            return [""];
                        }
                    }).catch(function (err) {
                        console.error(err);
                        return "";
                    });
            },
            "view_remoteItem_search": function search(jseditor_editor, input) {
                var url = new URL('terriajs/search?'+
                        'resource_name='+ encodeURI(input)+
                        '&dataset_title='+ encodeURI(input)+
                        '&dataset_description='+ encodeURI(input),jsonschema.ckanUrl);
                if (input.length < 2) {
                    return [];
                }
                return fetch(url).then(function (request) {
                        if (request.status === 200) {
                            return request
                            .json()
                            .then(results => results.filter(el => el.config[jsonschema.typeKey] != "terriajs-group" && el.config[jsonschema.typeKey] != "group"))
                        } else {
                            return [""];
                        }
                    }).catch(function (err) {
                        console.error(err);
                        return "";
                    });
            },
            "view_remoteGroup_search": function search(jseditor_editor, input) {
                var url = new URL('terriajs/search?'+
                        'resource_name='+ encodeURI(input)+
                        '&dataset_title='+ encodeURI(input)+
                        '&dataset_description='+ encodeURI(input),jsonschema.ckanUrl);
                if (input.length < 2) {
                    return [];
                }
                return fetch(url).then(function (request) {
                        if (request.status === 200) {
                            return request
                            .json()
                            .then(results => results.filter(el => el.config[jsonschema.typeKey] == "terriajs-group" || el.config[jsonschema.typeKey] == "group"))
                        } else {
                            return [""];
                        }
                    }).catch(function (err) {
                        console.error(err);
                        return "";
                    });
            },
            "view_renderer": function(jseditor_editor, result, props) {

                const resource_url = new URL('dataset/' + result.package_id + '/resource/' + result.resource_id, jsonschema.ckanUrl);

                return jsonschema.dataDict.id == result.id ? '':
                    ['<li ' + props + ' data-toggle="tooltip" data-placement="bottom" title="'+ result.id +'" >',
                        '<div class="eiao-object-title">',
                            '<div>',
                                '<b>',
                                    '<a target=”_blank” href="'+ resource_url +'">Resource</a>',
                                '</b>',
                            '</div>',
                            '<div>',
                                    result.resource_name || 'Unnamed resource',
                                '<small> ',
                                    result.resource_description && result.resource_description.substring(0,150),
                                '</small>',
                            '</div>',
                        '</div>',
                        '<div class="eiao-object-snippet">',
                            '<div>',
                                '<b>',
                                    'From dataset:',
                                '</b>',
                            '</div>',
                            '<div>',
                                    result.dataset_title || 'Unnamed dataset',
                                '<small> ',
                                    result.dataset_description && result.dataset_description.substring(0,150),
                                '</small>',
                            '</div>',
                        '</div>',
                        '<div class="eiao-object-title">',
                            '<div>',
                                '<b>',
                                    'From Organization:',
                                '</b>',
                            '</div>',
                            '<div>',
                                    result.organization_title || 'Unnamed organization',
                            '</div>',
                        '</div>',
                    '</li>'].join('');
            },
            "view_getValue": function getResultValue(jseditor_editor, result) {
                return result.id
            },
            "view_remote_getValue": function getResultValue(jseditor_editor, result) {
                
                // set also the name
                var name_path = jseditor_editor.path.split('.').slice(0, -1)
                name_path.push('name')
                name_path = name_path.join('.')
                
                // var name_value = result.resource_name + " - " + result.dataset_title
                var name_value = result.dataset_title
                
                jsonschema.setValue(name_path, name_value)

                return new URL('terriajs/item/' + result.id +'.json', jsonschema.ckanUrl)
            },
        }
    };
}