import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
_ = toolkit._
from requests.models import InvalidURL
import json

import ckanext.terriajs.constants as constants
import ckanext.terriajs.utils as utils
# import ckanext.terriajs.logic.get as get
# import ckanext.terriajs.validators as v
import logging
log = logging.getLogger(__name__)


def read_all_template():
    return utils._read_all_json(constants.PATH_TEMPLATE)

def read_all_schema():

    _dict = utils._read_all_json(constants.PATH_SCHEMA)
    
    # let's also resolve remote schemas
    # TODO warning an appropriate template matching the schema should be provided
    for type in constants.FORMATS:
        if h.is_url(constants.TYPE_MAPPING[type]):
            # TODO better manage error conditions with appropriate http code and message
            _dict[type]=json.loads(requests.get(constants.TYPE_MAPPING[type]).content)

    return _dict


# TODO DOCUMENT (Default mapping)

def map_resource_to_terriajs_type(resource):
    '''
    returns a terriajs type based over resoure[format] 
    '''
    if not resource:
        raise Exception(_('The resource is None!'))

    resource_type = resource.get('format')
    if not resource_type:
        raise Exception(_('The resource has no format!'))

    # TODO Document why lower()
    resource_type = resource_type.lower()
    
    return map_resource_format_to_terriajs_type(resource_type)
    
def map_resource_format_to_terriajs_type(resource_type):
    '''
    if not found rise exception
    '''
    # type has been properly configured only if it is matching the type-mapping
    if not resource_type or resource_type not in constants.TYPE_MAPPING.keys():
        raise Exception(_('Not recognized type: {}. Please check your configuration.').format(resource_type))

    return resource_type

import requests
InvalidURL = requests.models.InvalidURL

def get_config(type):
    if not type:
        return None

    return constants.JSON_CATALOG[constants.TERRIAJS_CONFIG_KEY].get('{}.json'.format(type))

def get_schema(type):
    if not type:
        return None

    filename = constants.TYPE_MAPPING.get(type)
    if not filename:
        # not present in type_mapping but can be present into the catalog as json file
        filename = type
    return constants.JSON_CATALOG[constants.TERRIAJS_SCHEMA_KEY].get(filename)


import sys
_py3=False
if (sys.version_info > (3, 0)):
    _py3=True
import jinja2
Environment = jinja2.environment.Environment
FunctionLoader = jinja2.loaders.FunctionLoader 
TemplateSyntaxError = jinja2.TemplateSyntaxError

# from jinja2.utils import select_autoescape
def interpolate_fields(model, template):
    ###########################################################################
    # Jinja2 template
    ###########################################################################
    

    # template = view_config and Template(Markup(get_or_bust(view_config,constants.TERRIAJS_CONFIG).decode('string_escape')))
    # config = template and template.render(model)
    # try:
    #     # decode needed for python2.7
    #     config = view_config and json.loads(config)
    #     if not config:
    #         raise Exception(_('No config found for view: {}'.format(str(view_id))
    # except Exception as ex:
    #     raise Exception(_('Unable to parse resulting object should be a valid json:\n {}'.format(str(config),
    #     '\nException: '+str(ex)+
    #     '\nPlease check your template.'))



    _temp = dict(template)

    # for f in constants.FIELDS_TO_SKIP:
    #     if f in _temp:
    #         del _temp[f]
    import ckan.lib.navl.dictization_functions as dict_func
    
    # try:
    #     _template = env.get_template(_temp)
    #     _template.render(model)
    #     template = unflatten()
    # except TemplateSyntaxError as e:
    #     raise Exception(_('Unable to interpolate \'{}\' line \'{}\''.format(template,str(e.lineno))))
    # except Exception as e:
    #     raise Exception(_('Unable to interpolate \'{}\': {}'.format(template,str(e))))

    def functionLoader(name):
        return template[name]

    env = Environment(
                loader=FunctionLoader(functionLoader),
                # autoescape=select_autoescape(['html', 'xml']),
                autoescape=True,
                #newline_sequence='\r\n',
                trim_blocks=False,
                keep_trailing_newline=True)

    # _temp=dict_func.flatten_dict(template)
    # for f in _temp.keys():
    #     tbs=False #to be skipped
    #     for skip in constants.FIELDS_TO_SKIP:
    #         if skip in f:
    #             tbs=True
    #             break
    #     if tbs:
    #         continue
    # TODO check python3 compatibility 'unicode' may disappear?
    #     if isinstance(_temp[f],(str,unicode)):
    #         try:
    #             _template = env.get_template(f)
    #             _temp[f] = _template.render(model)
    #         except TemplateSyntaxError as e:
    #             raise Exception(_('Unable to interpolate field \'{}\' line \'{}\''.format(f,str(e.lineno))))
    #         except Exception as e:
    #             raise Exception(_('Unable to interpolate field \'{}\': {}'.format(f,str(e))))

    # return dict_func.unflatten(_temp)

    for f in template.keys():
        if f in constants.FIELDS_TO_SKIP:
            continue
        

        interpolate = False

        if _py3:
            # TODO check python3 compatibility 'unicode' may disappear?
            if isinstance(template[f],(str)):
                interpolate = True
        elif isinstance(template[f],(str,unicode)):
                interpolate = True
        
        if interpolate:
            try:
                _template = env.get_template(f)
                template[f] = _template.render(model)
            except TemplateSyntaxError as e:
                raise Exception(_('Unable to interpolate field \'{}\' line \'{}\'\nError:{}'.format(f,str(e.lineno),str(e))))
            except Exception as e:
                raise Exception(_('Unable to interpolate field \'{}\': {}'.format(f,str(e))))

    return template
    ###########################################################################