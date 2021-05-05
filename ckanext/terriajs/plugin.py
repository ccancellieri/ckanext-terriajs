import ckan.plugins.toolkit as toolkit

import logging
import json as json
#from jsonschema import RefResolver

import ckan.plugins as p


import constants
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

    # def update_config(self, config):
    #     p.toolkit.add_public_directory(config, 'theme/public')
    #     p.toolkit.add_template_directory(config, 'theme/templates')
    #     p.toolkit.add_resource('theme/public', 'ckanext-cesiumpreview')

    def configure(self, config):
        self.proxy_is_enabled = config.get('ckan.resource_proxy_enabled', False)
        # TERRIAJS_SCHEMA_URL
        # self.terriajs_url = config.get(*constants.TERRIAJS_URL)
        
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
                'terriajs_config': [not_empty]
            }
        }

    def can_view(self, data_dict):
        resource = data_dict['resource']
        format_lower = resource['format'].lower()
        if format_lower:
            format_lower = os.path.splitext(resource['url'])[1][1:].lower()
#        print format_lower
        if format_lower in constants.FORMATS:
            return True
        return False

    def setup_template_variables(self, context, data_dict):

        _dict = data_dict.copy()
        resource_view = _dict['resource_view']
        config_view = {}

        terriajs_schema=requests.get(config.get(*constants.TERRIAJS_SCHEMA_URL)).content
        if terriajs_schema:
            terriajs_schema=json.loads(terriajs_schema)

        terriajs_config=None
        if 'terriajs_config' in resource_view:
            terriajs_config=json.loads(resource_view.get('terriajs_config',{}))
        else:
            terriajs_config = json.loads('''{
               "catalog":[
                  {
                     "name":"",
                     "type":"group",
                     "order":1,
                     "description":"",
                     "preserveOrder":true,
                     "items":[]
                  }
               ],
               "homeCamera":{
                  "west":-180,
                  "east":180,
                  "north":90,
                  "south":-90
               }
            }''')

        config_view['config_view'] = {
            'terriajs_url': config.get(*constants.TERRIAJS_URL),
            'terriajs_schema': terriajs_schema,
            'terriajs_config': terriajs_config
        }
        _dict.update(config_view)
        return _dict

    def view_template(self, context, data_dict):
        return 'terriajs.html'

    def form_template(self, context, data_dict):
        return 'terriajs_form.html'
