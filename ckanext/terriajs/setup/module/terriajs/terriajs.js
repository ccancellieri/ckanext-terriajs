export const initialize = () => {
    window.JSONEditor.defaults.callbacks = {
        // "button":  function view_info(jseditor_editor, input){
        //         console.log(input);
        // },
        "template": {
            "view_template": (jseditor,e) => {

                if (!e || !e.id || e.id == '' || !isValidUUID(e.id)) {
                    return "Please set a view id";
                }
                
                var url = new URL('terriajs/describe?view_id='+e.id, jsonschema.ckanUrl);
                var request = new XMLHttpRequest();
                request.open('GET', url, false);  // `false` makes the request synchronous
                request.send(null);

                if (request.status === 200) {
                    const res = JSON.parse(request.response);
                    return res.resource_name+" - "+res.dataset_title;
                } else {
                    console.error("Unable to resolve item: "+e.id+".\n Response: "+request.response);
                    return "";
                }
                
                // asynch ???
                /*return fetch(url).then(function (response) {
                        return response.json();
                    }).then(function (data) {
                        resolve(data);
                    }).catch(function (err) {
                        console.error(err);
                        return "";
                    });;*/
            }
        },
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
            "view_renderer": function(jseditor_editor, result, props) {
                return terriajs.resource_view.id == result.id ? '':
                    ['<li ' + props + ' data-toggle="tooltip" data-placement="bottom" title="'+ result.id +'" >',
                        '<div class="eiao-object-title">',
                            '<div>',
                                '<b>',
                                    '<a target=”_blank” href="'+new URL('/terriajs/config/'+result.id+'.json', jsonschema.ckanUrl)+'">Resource</a>',
                                '</b>',
                            '</div>',
                            '<div>',
                                '<b>',
                                    result.resource_name || 'Unnamed resource',
                                '</b>',
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
                                '<b>',
                                    result.dataset_title || 'Unnamed dataset',
                                '</b>',
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
                                '<b>',
                                    result.organization_title || 'Unnamed organization',
                                '</b>',
                            '</div>',
                        '</div>',
                    '</li>'].join('');
            },
            "view_getValue": function getResultValue(jseditor_editor, result) {
                return result.id
            }
        }
    };
}