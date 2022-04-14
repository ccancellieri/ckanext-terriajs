
import copy

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

_ = toolkit._
g = toolkit.g
config = toolkit.config
import logging
import os

import ckanext.jsonschema.constants as _c
import ckanext.jsonschema.interfaces as _i
import ckanext.jsonschema.tools as _t
import ckanext.jsonschema.utils as _u
import ckanext.jsonschema.validators as _v
import ckanext.jsonschema.view_tools as _vt
import ckanext.terriajs.constants as _tc
import ckanext.terriajs.logic.get as get
from ckan.common import request
from flask import abort

get_validator = toolkit.get_validator
not_empty = get_validator('not_empty')
ignore_empty = get_validator('ignore_empty')


log = logging.getLogger(__name__)

class TerriajsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    #p.implements(p.IConfigurable)
    p.implements(p.IBlueprint)
    #p.implements(p.IResourceUrlChange)
    # p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IResourceView)
    p.implements(_i.IJsonschemaView, inherit=True)

    #IActions
    def get_actions(self):
        actions = {
            #'resource_view_delete': delete.resource_view_delete, # TODO REMOVE
            #'resource_view_update': delete.resource_view_update
        }
        return actions


    # IBlueprint
    def get_blueprint(self):
        return get.terriajs

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ckanext-terriajs')

        self.config = _u._json_load(_tc.PATH_CONFIG, _tc.FILENAME_CONFIG)

    # IJsonschemaView
    def register_jsonschema_resources(self):
        
        _t.add_schemas_to_catalog(_tc.PATH_SCHEMA)
        log.info('Registered schemas into jsonschema\'s registry')

        _t.add_templates_to_catalog(_tc.PATH_TEMPLATE)
        log.info('Registered templates into jsonschema\'s registry')
        
        _t.add_modules_to_catalog(_tc.PATH_MODULE)
        log.info('Registered modules into jsonschema\'s registry')

        _t.add_to_registry(_tc.PATH_REGISTRY, _tc.FILENAME_REGISTRY)
        log.info('Added terriajs registry entries to into jsonschema\'s registry')


    def resolve(self, view_body, view):

        force = request.args.get('force', 'false').lower() == 'true' # cast to boolean
        force_to = request.args.get('force_to', 'false').lower() == 'true'

        
        model = _vt._get_model(view.get('package_id'), view.get('resource_id'))
        view_opt = _vt.get_view_opt(view)
        model.update({
            _tc.TYPE :{'base_url': view_opt.get('base_url') } # TODO replace with opt.base_url?? 
        })

        _terriajs_config = _vt.interpolate_fields(model, view_body)     

        _config = get.resolve(_terriajs_config, force, force_to)
        return _config


    def wrap_view(self, view_body, view):
               
        view_opts = _vt.get_view_opt(view)

        camera={
            'east': view_opts.get('east',180),
            'west': view_opts.get('west',-180),
            'north': view_opts.get('north',90),
            'south': view_opts.get('south',-90)
        }

        # TODO: This is because we don't have a proper registration of terriajs items into the registry
        # Replace with get_template_of

        _config = copy.deepcopy(_t.get_template_of(_tc.CATALOG_TYPE))
        _config['catalog'].append(view_body)
        _config.update({'homeCamera': camera})

        return _config

    # IDomainObjectModification
    # def notify(self, entity, operation):
    #     #TODO register view delete notification (not watched by this)
    #     u'''
    #     Send a notification on entity modification.
    #     :param entity: instance of module.Package.
    #     :param operation: 'new', 'changed' or 'deleted'.
    #     '''
    #     # if not isinstance(entity, model.Package):
    #     #     return

    #     # log.debug('Notified of package event: %s %s', entity.name, operation)
    #     pass
    
    #IResourceUrlChange
    # def notify(self, resource):
    #     # Receives notification of changed URL on a resource.
    #     # NOTE: this is not needed: Using templates and resolving at runtime the url.
    #     pass

    # IResourceView
    def info(self):
    
        # TODO DO WE NEED THIS?
        def default_config(plugin_name):
            return _vt.get_opt(self.config)
    
        info = {
            u'iframed': False,
            u'name': _tc.TYPE,
            u'schema': {
                _c.SCHEMA_TYPE_KEY: [not_empty], # import
                _c.SCHEMA_BODY_KEY: [not_empty, _v.view_schema_check],
                _c.SCHEMA_OPT_KEY: [default_config],
                "selected_jsonschema_type": [ignore_empty]
            },
            u'requires_datastore': False
        }
            
        plugin_info = _vt.get_info(self.config)

        info.update(plugin_info)

        return info
    

    def can_view(self, data_dict):

        resource = data_dict.get('resource', None)
        
        resource_format = resource.get('format')
        resource_jsonschema_type = _t.get_resource_type(resource)
        
        view_configuration = _vt.get_view_configuration(self.config, resource_format, resource_jsonschema_type)
            
        if view_configuration:
            return True

        return False
        

    def setup_template_variables(self, context, data_dict):
    #TODO Do we need this? Could conflict with package's setup_template_variables
            # TODO MOVE IN JSONSCHEMA PLUGIN

        resource_view = data_dict.get('resource_view', {})

        view_jsonschema_type = _vt.get_view_type(resource_view)
        view_body = _t.as_dict(_vt.get_view_body(resource_view))
        view_opt = _t.as_dict(_vt.get_view_opt(resource_view))

        if not view_jsonschema_type: # the view doesn't exist

            resource = data_dict.get('resource')
            resource_format = resource.get('format')
            resource_jsonschema_type = _t.get_resource_type(resource)

            view_configuration =_vt.get_view_configuration(self.config, resource_format, resource_jsonschema_type)
            
            # we force the first jsonschema type, even if there are more matches
            view_jsonschema_type = view_configuration.get(_c.VIEW_JSONSCHEMA_TYPE)[0]
            view_body = _t.as_dict(_t.get_template_of(view_jsonschema_type))
            view_opt = _t.as_dict(_vt.get_opt(self.config))


        try:
            resource_view = data_dict.get('resource_view')
            resource_view.update({
                    _c.SCHEMA_TYPE_KEY: view_jsonschema_type,
                    _c.SCHEMA_BODY_KEY: view_body,
                    _c.SCHEMA_OPT_KEY: view_opt,
                    _c.JSON_SCHEMA_KEY: _t.get_schema_of(view_jsonschema_type)
                })

            return data_dict
        except Exception as e:
            abort(404, e.message)
    
    def view_template(self, context, data_dict):
        return 'terriajs.html'

    def form_template(self, context, data_dict):
        return 'terriajs_form.html'
