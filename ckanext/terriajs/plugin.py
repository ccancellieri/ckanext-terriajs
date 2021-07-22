from requests.models import InvalidURL
import ckan.plugins.toolkit as toolkit

import logging
import json as json
# from ckan.common import json
#from jsonschema import RefResolver

import ckan.plugins as p

import copy
import ckanext.terriajs.constants as constants
import ckan.logic.validators as v

import requests
import ckan.lib.helpers as h

log = logging.getLogger(__name__)

_ = toolkit._
g = toolkit.g
config = toolkit.config

not_empty = p.toolkit.get_validator('not_empty')
#ignore_missing = p.toolkit.get_validator('ignore_missing')
#ignore_empty = p.toolkit.get_validator('ignore_empty')
is_boolean = p.toolkit.get_validator('boolean_validator')


# https://docs.ckan.org/en/2.8/extensions/validators.html#ckan.logic.validators.json_object
# NOT FOUND import ckan.logic.validators.json_object
#json_object = p.toolkit.get_validator('json_object')

import ckanext.terriajs.logic.get as get

import ckan.lib.navl.dictization_functions as df

missing = df.missing
StopOnError = df.StopOnError
Invalid = df.Invalid

def default_type(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    type = data.get(key)
    if not type or type is missing:
        resource = _instance_to_dict(context['resource'])
        type = _get_view_type(resource)
        if not type:
            errors[key].append(_('Missing value'))
            raise StopOnError

        data[key] = type

def default_synch(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    synch = data.get(key)
    if not synch or synch is missing:
        data[key] = 'dataset'
    

def default_config(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    config = data.get(key)
    if not config or config is missing:
        resource = context['resource']
        _resource = _instance_to_dict(resource)
        # _resource.update({ 'type': _get_view_type(resource)})
        
        config = _get_config(_resource)
        if not config:
            errors[key].append(_('Missing value'))
            raise StopOnError
        data[key] = config

def default_lon_e(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=180
        return
    try:
        if int(data[key])>180:
            data[key]=180
    except ValueError:
        data[key]=180

def default_lon_w(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-180
        return
    try:
        if int(data[key])<-180:
            data[key]=-180
    except ValueError:
        data[key]=-180

def default_lat_n(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=90
        return
    try:
        if int(data[key])>90:
            data[key]=90
    except ValueError:
        data[key]=90

def default_lat_s(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-90
        return
    try:
        if int(data[key])<-90:
            data[key]=-90
    except ValueError:
        data[key]=-90
    
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

def _instance_to_dict(i):
    # EXTENSION POINT
    # TODO WARNING
    # resource = i.__dict__
    # if resource.get('url_type') == 'upload':
    #     resource['url'] = h.url_for(
    #                                 controller='package',
    #                                 action='resource_download',
    #                                 id=resource['package_id'],
    #                                 resource_id=resource['id'],
    #                                 filename=resource['url'],
    #                                 qualified=True)
    #     resource['url_type']='link'

    # return resource
    resource = {'name': i.name or '',
                'url': i.url or '',
                'description': i.description or '',
                'id': i.id or '',
                'package_id': i.package_id or '',
                'format': (i.format or '').lower()
    }
    if i.url_type == 'upload':
        resource['url'] = h.url_for(
                                    controller='package',
                                    action='resource_download',
                                    id=resource['package_id'],
                                    resource_id=resource['id'],
                                    filename=resource['url'],
                                    qualified=True)
    return resource

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

    def configure(self, config_):
        with open(constants.SCHEMA_TYPE_MAPPING_FILE) as f:
            constants.TYPE_MAPPING = json.load(f)
        constants.FORMATS=constants.TYPE_MAPPING.keys()

        
    def notify(self, resource):
        # Receives notification of changed URL on a resource.
        #TODO update the view model with the new url
        pass

    def info(self):
        # log.warn("---------------->"+_(config.get(*constants.DEFAULT_TITLE)))
        return {
            u'icon': constants.ICON,
            u'name': constants.NAME,
            u'title': _(constants.DEFAULT_TITLE),
            u'default_title': _(constants.DEFAULT_TITLE),
            u'always_available': constants.ALWAYS_AVAILABLE,
            u'iframed': False,
            #u'filterable': False,
            u'preview_enabled': False,
            u'full_page_edit': True,
            u'schema': {
                #'__extras': [ignore_empty]
                #'terriajs_config': [not_empty, json_object]
                'terriajs_type': [default_type, not_empty],
                'terriajs_synch': [default_synch, not_empty],
                'terriajs_config': [default_config, not_empty],
                'west':[default_lon_w],
                'east':[default_lon_e],
                'north':[default_lat_n],
                'south':[default_lat_s]
            }
        }

    def can_view(self, data_dict):
        resource = data_dict.get('resource',None)
        return _get_view_type(resource) in constants.DEFAULT_FORMATS

    def setup_template_variables(self, context, data_dict):

        _dict = copy.deepcopy(data_dict)

        resource_view = _dict['resource_view']

        resource = _dict.get('resource',None)

        resource_type = resource_view.get('terriajs_type',_get_view_type(resource))

        terriajs_schema = resource_view.get('terriajs_schema', get.mapping(resource_type))
        if not terriajs_schema:
            raise InvalidURL(resource_type+_(' not defined, check your config'))
        
        terriajs_config=resource_view.get('terriajs_config',_get_config(resource))
        
        # synch_resource
        config_view = {}
        config_view['config_view'] = {
            # TODO remove 'terriajs_' prefix (also js and html)
            'terriajs_url': constants.TERRIAJS_URL,
            'terriajs_schema': json.loads(terriajs_schema),
            'terriajs_config': terriajs_config,
            'terriajs_type': resource_type,
            'terriajs_synch': _get_synch(resource_view),
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

# TODO DOCUMENT (Default mapping)
def _get_view_type(resource):
    resource_type = resource.get('format','').lower()
    # type has been configured, is it matching into the config?
    if resource_type not in constants.TYPE_MAPPING.keys():
        resource_type = constants.DEFAULT_TYPE
    
    return resource_type



def _get_synch(resource_view):

    # if terriajs_synch is not 'none':
    #     if terriajs_synch is not 'resource':
    #         terriajs_config['name']=resource.get('name',terriajs_config['name'])
    #         terriajs_config['description']=resource.get('description',terriajs_config['description'])
    #     elif terriajs_synch is not 'dataset':
    #         dataset = data_dict.get('package',None)
    #         terriajs_config['name']=dataset.get('name',terriajs_config['name'])
    #         terriajs_config['description']=dataset.get('notes',terriajs_config['description'])
    #     else:
    #         raise Exception(_("Unsupported synch mode: ")+str(terriajs_synch))

    return resource_view.get('terriajs_synch','none')

def _get_config(resource):
    
        # generate base configuration

    terriajs_config= None
    resource_type = _get_view_type(resource)

    if resource_type == constants.DEFAULT_TYPE:
        terriajs_config = constants.TERRIAJS_CONFIG
    else:
        # package=data_dict.get('package','')
        terriajs_config = {
                        'name': resource.get('name',''),
                        'url': resource.get('url',''),
                        'description': resource.get('description',''),
                        'id': resource.get('id',''),
                        'type': resource_type or ''
                    }

###################################################            
# TODO : EXTENSION POINT TO CONFIGURE BASED ON TYPE
###################################################

    if resource_type=='wms':
        terriajs_config.update({'layers': resource.get('name','')})
    elif resource_type=='wmts':
        terriajs_config.update({'layer': resource.get('name',''),
                            "useResourceTemplate": False,
                            "ignoreUnknownTileErrors": True,
                            "treat403AsError": False,
                            "treat404AsError": False,
                            "isLegendVisible": False})

    elif resource_type==constants.LAZY_GROUP_TYPE:
        terriajs_config.update({'items': []})
    
    # TODO BBOX based on the layer...
    
    return json.dumps(terriajs_config)
