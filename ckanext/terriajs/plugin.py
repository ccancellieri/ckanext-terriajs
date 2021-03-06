
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
_ = toolkit._
g = toolkit.g
config = toolkit.config

import json
import copy
import ckan.model as model
import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools
import ckanext.terriajs.logic.get as get
import ckanext.terriajs.logic.delete as delete
import ckanext.terriajs.validators as v
import logging
log = logging.getLogger(__name__)

class TerriajsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(p.IResourceView)
    p.implements(p.IBlueprint)
    #p.implements(p.IResourceUrlChange)
    # p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.IActions)

    #IActions
    def get_actions(self):
        actions = {
            'resource_view_delete': delete.resource_view_delete,
            'resource_view_update': delete.resource_view_update
        }
        return actions

    #IDomainObjectModification
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

    # IBlueprint
    def get_blueprint(self):
        return get.terriajs

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ckanext-terriajs')
    
    def configure(self, config_):
        with open(constants.SCHEMA_TYPE_MAPPING_FILE) as f:
            constants.TYPE_MAPPING = json.load(f)
        constants.FORMATS=constants.TYPE_MAPPING.keys()

        # Append all the rest of the available schemas
        constants.JSON_CATALOG.update({
                constants.TERRIAJS_SCHEMA_KEY:tools.read_all_schema(),
                constants.TERRIAJS_CONFIG_KEY:tools.read_all_template()
            })

        for format in constants.FORMATS:
            if not tools.get_schema(format):
                raise Exception(_('Unable to find schema for format {}'.format(format)))
            if not tools.get_config(format):
                raise Exception(_('Unable to find template for format {}'.format(format)))

        # a remote schema may correspond to a remote template which is still not possible
        # template mapping is missing we r using direct filame to terriajs_type mapping

    
    def info(self):
        return {
            u'icon': constants.ICON,
            u'name': constants.TYPE,
            u'title': _(constants.DEFAULT_TITLE),
            u'default_title': _(constants.DEFAULT_TITLE),
            u'always_available': constants.ALWAYS_AVAILABLE,
            u'iframed': False,
            #u'filterable': False,
            u'preview_enabled': False,
            u'full_page_edit': True,
            u'schema': {
                #'__extras': [ignore_empty]
                constants.TERRIAJS_TYPE_KEY: [v.default_type, v.not_empty],
                constants.TERRIAJS_CONFIG_KEY: [v.default_config, v.not_empty,v.config_schema_check],
                'west':[v.default_lon_w],
                'east':[v.default_lon_e],
                'north':[v.default_lat_n],
                'south':[v.default_lat_s]
            }
        }

    def can_view(self, data_dict):
        resource = data_dict.get('resource',None)
        try:
            return tools.map_resource_to_terriajs_type(resource) in constants.DEFAULT_FORMATS
        except Exception as e:
            return False
        

    def setup_template_variables(self, context, data_dict):

        _dict = copy.deepcopy(data_dict)

        resource_view = _dict['resource_view']

        resource = _dict.get('resource',None)

        terriajs_type = resource_view.get(constants.TERRIAJS_TYPE_KEY,tools.map_resource_to_terriajs_type(resource))
        
#TODO trap exception here and return error correctly

        terriajs_schema = resource_view.get(constants.TERRIAJS_SCHEMA_KEY, tools.get_schema(terriajs_type))
        
        terriajs_config=resource_view.get(constants.TERRIAJS_CONFIG_KEY, tools.get_config(terriajs_type))
        
        config_view = {}
        config_view['config_view'] = {
            # TODO remove 'terriajs_' prefix (also js and html)
            constants.TERRIAJS_URL_KEY: constants.TERRIAJS_URL,
            constants.TERRIAJS_SCHEMA_KEY: terriajs_schema,
            constants.TERRIAJS_CONFIG_KEY: terriajs_config,
            constants.TERRIAJS_TYPE_KEY: terriajs_type,
            # 'terriajs_synch': _get_synch(resource_view),
            'west': -180,
            'east': 180,
            'north': 90,
            'south': -90
        }
        _dict.update(config_view)
        return _dict
    
    def view_template(self, context, data_dict):
        return 'terriajs.html'

    def form_template(self, context, data_dict):
        return 'terriajs_form.html'
