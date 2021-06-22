from requests.models import InvalidURL
import ckan.plugins.toolkit as toolkit

import logging
import json as json
#from jsonschema import RefResolver

import ckan.plugins as p

import copy
import ckanext.terriajs.constants as constants
import ckan.logic.validators as v

import requests
import ckan.lib.helpers as h
from ckan.common import json
import json as _json
try:
    import os
    import ckanext.resourceproxy.plugin as proxy
except ImportError:
    pass

log = logging.getLogger(__name__)

_ = toolkit._
g = toolkit.g
config = toolkit.config

not_empty = p.toolkit.get_validator('not_empty')
#ignore_missing = p.toolkit.get_validator('ignore_missing')
#ignore_empty = p.toolkit.get_validator('ignore_empty')


# https://docs.ckan.org/en/2.8/extensions/validators.html#ckan.logic.validators.json_object
# NOT FOUND import ckan.logic.validators.json_object
#json_object = p.toolkit.get_validator('json_object')

import ckanext.terriajs.logic.get as get


def resolve_mapping(type):
    '''
    try to resolve the url from the schema-mapping configuration.
    return an url
    '''
    if type in constants.TYPE_MAPPING:
        if not h.is_url(constants.TYPE_MAPPING[type]):
            return h.url_for('/terriajs/mapping/'+str(type), _external=True)
        else:
            return constants.TYPE_MAPPING[type]
    else:
        raise InvalidURL(_("Type "+type+" not found into available mappings, please check your configuration"))



class TerriajsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(p.IResourceView)
    p.implements(p.IResourceUrlChange)
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return get.terriajs
    
    proxy_is_enabled = False
    terriajs_url = None

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ckanext-terriajs')
        # TERRIAJS_SCHEMA_URL
        # self.terriajs_url = config.get(*constants.TERRIAJS_URL)
        schema_mapping_file=config.get('ckanext.terriajs.schema.type_mapping','./type-mapping.json')
        with open(schema_mapping_file) as f:
            constants.TYPE_MAPPING = json.load(f)

        constants.FORMATS=constants.TYPE_MAPPING.keys()

    def configure(self, config):
        self.proxy_is_enabled = config.get('ckan.resource_proxy_enabled', False)
        self.formats = constants.FORMATS
        
    def notify(self, resource):
        # Receives notification of changed URL on a resource.
        #TODO update the view model with the new url
        pass

    def info(self):
        # log.warn("---------------->"+_(config.get(*constants.DEFAULT_TITLE)))
        return {
            u'icon': config.get(*constants.ICON),
            u'name': constants.NAME,
            u'title': _(config.get(*constants.DEFAULT_TITLE)),
            u'default_title': _(config.get(*constants.DEFAULT_TITLE)),
            u'always_available': config.get(*constants.ALWAYS_AVAILABLE),
            u'iframed': False,
            #u'filterable': False,
            u'preview_enabled': False,
            u'full_page_edit': True,
            u'schema': {
                #'__extras': [ignore_empty]
                #'terriajs_config': [not_empty, json_object]
                'terriajs_config': [not_empty],
                'terriajs_type': [not_empty]
            }
        }

    def can_view(self, data_dict):
        resource = data_dict.get('resource',None)
        if resource:
            format_lower = resource.get('format','').lower()
            return format_lower in constants.FORMATS
        return False

    def setup_template_variables(self, context, data_dict):

        _dict = copy.deepcopy(data_dict)
        resource_view = _dict['resource_view']
        config_view = {}
        
        resource = data_dict.get('resource',None)

        full_catalog = False
        if resource and 'format' in resource:
            resource_type = resource[u'format'].lower()

            # type has been configured, is it matching into the config?
            if resource_type not in constants.TYPE_MAPPING.keys():
                resource_type = constants.DEFAULT_TYPE
        
        if resource_type == constants.DEFAULT_TYPE:
            full_catalog = True
        
        # if resource:    
        #     schema_url= resolve_mapping(resource_type.lower() or constants.DEFAULT_TYPE)

        # if not schema_url:
        #     raise InvalidURL(_('Invalid schema url'))

        terriajs_schema=get.mapping(resource_type)
        if not terriajs_schema:
            raise InvalidURL(resource_type+' not defined, check your config')

        terriajs_config=resource_view.get('terriajs_config',None)
        if not terriajs_config:
            # generate base configuration

###################################################            
# TODO : EXTENSION POINT TO CONFIGURE BASED ON TYPE
###################################################

            if full_catalog: # TODO base over type, remove flag
                terriajs_config=json.dumps(constants.TERRIAJS_CONFIG)
            else:
                terriajs_config=json.dumps({
                    'name': resource.get('name',''),
                    'url': resource.get('url',''),
                    'description': resource.get('description',''),
                    'id': resource.get('id',''),
                })

        config_view['config_view'] = {
            # TODO remove 'terriajs_' prefix (also js and html)
            'terriajs_url': config.get(*constants.TERRIAJS_URL),
            'terriajs_schema': json.loads(terriajs_schema),
            'terriajs_config': terriajs_config,
            'terriajs_type': resource_type
        }
        _dict.update(config_view)
        return _dict
    
    def view_template(self, context, data_dict):
        return 'terriajs.html'

    def form_template(self, context, data_dict):
        return 'terriajs_form.html'
