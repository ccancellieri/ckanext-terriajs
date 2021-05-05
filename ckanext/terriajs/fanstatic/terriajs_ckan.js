// json preview module
ckan.module('terriajs', function (jQuery, _) {
  terriajs = {
        preview: function (){
            let value=terriajs.editor.getValue();
            let catalog=terriajs.asObject(value);
            let iframe=document.getElementById('terriajs-iframe');
            if (iframe){
                let cat = iframe.contentWindow.viewState.terria.catalog;
                let groups = catalog;
                // groups.setPrototypeOf = 'Array';
                //groups.prototype = Array.protype
                //Object.setPrototypeOf(groups,Array.prototype)
                //cat.updateFromJson(groups);
                //iframe.contentWindow.postMessage('drop', cat)
                //iframe.contentWindow.postMessage(JSON.parse('{"initSources":["https://data.apps.fao.org"],"catalog":[{"description":"","items":[{"getRecordsTemplate":" full dc:subject AQUAMAPS_basins ","name":"Hydrological Basins","includeEsriMapServer":true,"url":"https://data.review.fao.org/map/catalog/srv/eng/csw","minimumMaxScaleDenominator":10000000000,"baseLink":"https://data.review.fao.org/map/catalog/srv/eng/catalog.search#/metadata/","filterByWmsGetCapabilities":false,"includeEsriFeatureServer":true,"includeWfs":true,"includeWms":true,"includeKml":true,"includeGeoJson":true,"type":"csw","groupBy":"organization","includeCsv":true},{"layers":"groundwateratlas:atlas_depth_groundwater","opacity":1,"name":"Estimated depth to groundwater (mbgl)","ignoreUnknownTileErrors":true,"url":"https://ggis.un-igrac.org/geoserver/wms","keepOnTop":true,"isLegendVisible":false,"type":"wms"},{"layers":"groundwateratlas:atlas_aquifer_productivity1","opacity":1,"name":"Aquifer productivity (l/s)","ignoreUnknownTileErrors":true,"url":"https://ggis.un-igrac.org/geoserver/wms","keepOnTop":true,"isLegendVisible":false,"type":"wms"},{"layer":"AAFC/ACI/2009","name":"AAFC/ACI/2009","url":"https://api.data.review.fao.org/api/v1/proxy/https://gee-wmts-review-p3zkzgnl5q-uc.a.run.app/GetTile?layer=AAFC/ACI/2009&TileMatrix={z}&TileRow={y}&TileCol={x}","type":"url-template","keepOnTop":true,"treat404AsError":false,"maximumZoom":10,"__fillColor":"no-specified","lineColor":"rgb(255, 0, 0)","treat403AsError":false,"rectangle":[-180,-85.051129,180,83.658333],"forceProxy":false}],"preserveOrder":true,"type":"group","order":1,"name":""}],"homeCamera":{"west":-180,"east":180,"north":90,"south":-90}}'))
            }

        },
        asObject: function (value) {
            try {
                if (value){
                    if (typeof value == "string"){
                        return JSON.parse(value);
                    } else {
                        return value;
                    }
                }
            } catch (err) {
                console.log(err.stack);
            }
            return {};
        },
        asString: function (value) {
            if (value){
                if (typeof value == "string"){
                    return value;
                } else {
                    return JSON.stringify(value, null, '  ');
                }
            }
            return "";
        },
        onSubmit: function (event) {
                if (!this.editor) return;

                // prepare info to serialize
                let value=this.editor.getValue();
                this.terriajs_config=terriajs.asObject(value);

                let input=$('#terriajs_config')[0];
                input.value=terriajs.asString(value);

                this.editorToggle(enable=false);
        },
        ckan_url: undefined,
        terriajs_url: undefined,
        terriajs_schema: undefined,
        terriajs_config: undefined,
        editor: undefined,
        initialize: function () {
            var self = this;

//      var vis_server = 'http://localhost';  //local
//            var vis_server = 'https://data.review.fao.org/map/story';


            var package = self.options.package;
            var resource = self.options.resource;
            var resource_view = self.options.resourceView;
            var config_view = self.options.configView;

            terriajs.ckan_url = self.options.ckanUrl;
            terriajs.terriajs_url = config_view.terriajs_url;
            terriajs.terriajs_schema = config_view.terriajs_schema;
            terriajs.terriajs_config = config_view.terriajs_config;

            terriajs.preview=this.preview.bind(this);
            terriajs.getEditor=this.getEditor.bind(terriajs);
            terriajs.getEditorAce=this.getEditorAce.bind(terriajs);
            terriajs.editorReady=this.editorReady.bind(terriajs);
            terriajs.editorValidate=this.editorReady.bind(terriajs);
            terriajs.editorToggle=this.editorToggle.bind(terriajs);

            terriajs.wrap=this.wrap.bind(terriajs);
//terriajs.onSubmit
            $('.dataset-form').find('button[type=submit]').each(
                function (){$(this).on('click', terriajs.onSubmit.bind(terriajs));});

            terriajs.getEditorAce();
        },
        getEditorAce: function (){

            let value;
            if (this.editor && this.editor instanceof window.JSONEditor){
                // save changes in local context
                value=terriajs.asString(this.editor.getValue());
                this.editor.destroy();
            } else {
                // save changes in local context
                value=terriajs.asString(terriajs.terriajs_config);
            }

            let schema={
              "type": "string",
              "format": "json",
              "title": "Terria configuration",
              "options": {
                    "ace": {
                      //"theme": "ace/theme/tailwind",
                      "tabSize": 2,
                      "useSoftTabs": true,
                      "wrap": true,
                      //"fontFamily": "tahoma",
                      "fontSize": "14pt"
                      //,"enableBasicAutocompletion": true
                    }
               }
              }
        // Initialize the editor
            this.editor = new JSONEditor(document.getElementById('editor-terriajs-config'),{
                // Enable fetching schemas via ajax
                ajax: true,
                ajaxBase: terriajs.ckan_url,
//                ajaxCredentials: true

                // The schema for the editor
                schema: schema,

                // Seed the form with a starting value
                startval: value,

                // https://github.com/json-editor/json-editor#css-integration
                // barebones, html (the default), bootstrap4, spectre, tailwind
                theme: 'bootstrap4',
                iconlib: "fontawesome4"
                });
            /*JSONEditor.plugins.ace = {
                theme:"tailwind",
              fontFamily: "tahoma",
              fontSize: "12pt"
            };*/
terriajs.ajv = new Ajv({
coerceTypes: true,
                      loadSchema: function (uri) {
                            return new Promise((resolve, reject) => {
                                retry=3;
                                function get(retry, uri){
                                    //resolve(require('./id.json')); // replace with http request for example
                                        $.ajaxSetup({timeout: 30000});
                                        $.get( uri, function(data) {
                                          //alert( "success: ");
                                          resolve(data);
                                          return data;
                                        })
                                      .fail(function() {
                                        //alert( "error" );
                                        if (retry>0){
                                            get(--retry, uri);
                                        } else {
                                            reject(new Error(`could not locate ${uri}`));
                                        }
                                      });
                                  };
                              if (uri.startsWith('http')) {
                                get(3,uri);
                              } else {
                                //reject(new Error(`could not locate ${uri}`));
                                resolve(uri);
                              }
                            });
                      }
                });

            if (!terriajs.validate){
                terriajs.ajv.compileAsync(terriajs.terriajs_schema).then(
                    function(val){
                        terriajs.validate=val;
                        terriajs.editorOnChange(terriajs.ajvValidation());
                    }
                );
            }
            this.editor.on('ready',this.editorReady);
            this.editor.on('change',()=>{

                this.editorOnChange(terriajs.ajvValidation());
            });
            this.editorToggle(true);
        },
        ajvValidation: function () {

            // Get an array of errors from the validator
            if (!terriajs.editor || !terriajs.editor.ready){
                return;
            }

            var errors = undefined;
            try {
                let val=JSON.parse(terriajs.editor.getValue());
                if (terriajs.validate){
                    if (!terriajs.validate(val))
                        errors='<div style="height:150px; overflow:auto;" id="outher-error">'+
                            '<table id="inner-error" style="width:100%;">'+
                            '<tr">'+
                                '<th><h2>Message</h2></th>'+
                                '<th><h2>Path</h2></th>'+
                                '<th><h2>Error</h2></th></tr>'+
                                terriajs.validate.errors.map(
                                    e=>'<tr><td>'+
                                        e.message+'</td><td>'
                                        +e.dataPath+'</td><td>'
                                        +Object.keys(e.params).map(m=>m+' : '+e.params[m]).reduce((a,c)=>a+c,'')+'</td></tr>'
                                ).reduce((a,c,i)=>a+c,'')+
                            '</table></div>';
                }
                return {'html':errors, 'lock':false};
            } catch (exc) {
                errors='<p>'+exc+'</p>';
                return {'html':errors, 'lock':true};
            }

        },
        getEditor: function (){
            let schema = terriajs.terriajs_schema;

            let value;
            if (this.editor && this.editor instanceof window.JSONEditor){
                // save changes in local context
                value=terriajs.asObject(this.editor.getValue());
                this.editor.destroy();
            } else {
                // save changes in local context
                value=terriajs.asObject(terriajs.terriajs_config);
            }
            // Initialize the editor
            this.editor = new JSONEditor(document.getElementById('editor-terriajs-config'),{
                // Enable fetching schemas via ajax
                ajax: true,
                ajaxBase: terriajs.ckan_url,
//                ajaxCredentials: true

                // The schema for the editor
                schema: schema,

                // Seed the form with a starting value
                startval: value,

                // https://github.com/json-editor/json-editor#css-integration
                // barebones, html (the default), bootstrap4, spectre, tailwind
                theme: 'bootstrap4',
                iconlib: "fontawesome4"
                //,
                // Disable additional properties
                //no_additional_properties: true,

                // Require all properties by default
                //required_by_default: true
            });
            this.editor.on('ready',this.editorReady);
            this.editor.on('change',()=>{

                // Get an array of errors from the validator
                if (!terriajs.editor || !terriajs.editor.ready){
                    return;
                }
                // TODO call when instantiate -> refactor to function and call onReady
                var errors = terriajs.editor.validate();
                if (errors.lenght)
                    this.editorOnChange({'html':'<div id="outher-error">'+
                                errors.reduce(o=>'<p>'+o+'</p>','')+'</div>', 'lock':true});
                else
                    this.editorOnChange({'html':undefined, 'lock':true});

            });
            // TODO call validation when instantiate -> refactor to function
      },
      editorToggle: function (enable=false) {
            if(!this.editor) return;
            if(enable===true || !this.editor.isEnabled()) {
              this.editor.enable(true);
              $('#editor-toggle').html("Lock");

              let status = $('#editor-status-holder');
              status.css("color","green");
              status.html("unlocked");
            }
            else {
              this.editor.disable(false);
              $('#editor-toggle').html("Unlock");

              let status = $('#editor-status-holder');
              status.css("color","red");
              status.html("locked");
            }

      },
      wrap: function(func){
          try {
                func(arguments);
          } catch(err) {
            console.log(err.stack);
          } finally {
            event.preventDefault();
          }
      },
      editorReady: function () {
            terriajs.editor && terriajs.editor.ready && terriajs.editor.validate();
            this.editorToggle(true);
      },
      editorOnChange: function (i) {
            let errors=i.html;
            let lock=i.lock;
            var indicator = $('#editor-error-holder');

            // Not valid
            if(errors) {

                if (lock){
                    // lock the howto
                    $('#editor-howto').prop('disabled',true);
                    // lock the save button
                    $('.form-actions [name="save"]').prop('disabled',true);
                    indicator.css("color","red");
                } else {
                    // lock the howto
                    $('#editor-howto').prop('disabled',false);
                    // lock the save button
                    $('.form-actions [name="save"]').prop('disabled',false);
                    indicator.css("color","black");
                }
                indicator.html(errors);
                                        /*if (typeof o == 'object'){
                                            return Object.keys(o).map(k=>this(i,a));
                                        }else if (typeof o == 'Array'){
                                            return o.map(i=>this(i,a));
                                        }else {

                                        }*/

                //indicator.textContent = "not valid";
            }
            // Valid
            else {
                // un lock the save button
                $('.form-actions [name="save"]').prop('disabled',false);
                // un lock the howto
                $('#editor-howto').prop('disabled',false);
                indicator.html("<h3 style='display: inline; color: green;'>valid</h3>");
            }
        }
    };
    return terriajs;
});
