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

# def resolve_mapping(type):
#     '''
#     try to resolve the url from the schema-mapping configuration.
#     return an url
#     '''
    
#     if type in constants.TYPE_MAPPING:
#         if not h.is_url(constants.TYPE_MAPPING[type]):
#             return ''.join([h.url_for('/', _external=True),constants.REST_MAPPING_PATH,str(type)])
#         else:
#             return constants.TYPE_MAPPING[type]
#     else:
#         error = "Type "+type+" not found into available mappings, please check your configuration"
#         logging.log(logging.ERROR,error)
#         raise InvalidURL(_(error))

def read_template(name):
    '''
    provides a reader for local template definitions
    '''
    # TODO increase security should be/ensure to be under schema_path folder
    return utils._json_load(constants.PATH_TEMPLATE, name)

def read_schema(name):
    '''
    provides a reader for local schema definitions
    '''
    # TODO increase security should be/ensure to be under schema_path folder
    return utils._json_load(constants.PATH_SCHEMA, name)


# TODO DOCUMENT (Default mapping)

def map_resource_to_terriajs_type(resource):
    '''
    if not found fallbacks to DEFAULT_TYPE
    '''
    resource_type = resource.get('format')
    return map_resource_format_to_terriajs_type(resource_type)
    
def map_resource_format_to_terriajs_type(resource_type):
    '''
    if not found fallbacks to DEFAULT_TYPE
    '''
    if not resource_type:
        # TODO log
        return constants.DEFAULT_TYPE

    # TODO Document why lower()
    resource_type = resource_type.lower()

    # type has been properly configured only if it is matching the type-mapping
    if resource_type not in constants.TYPE_MAPPING.keys():
        resource_type = constants.DEFAULT_TYPE
    return resource_type

def default_template(terriajs_type):
    
    # generate base configuration
    # TODO create and use template mapping
    terriajs_config = read_template('{}.json'.format(terriajs_type))

    if terriajs_config:
        return terriajs_config
    else:
        # fallback, no template has been found
        #TODO LOG
        # return constants.TERRIAJS_CATALOG
        #FAIL FAST
        raise Exception(_('No valid template found for type: {}'.format(terriajs_type)))


import requests
InvalidURL = requests.models.InvalidURL

def resolve_schema_mapping(type):
    '''
    provides a proxy for local or remote url based on schema-mapping.json file and passed <type> param
    '''
    # try:
    if type in constants.TYPE_MAPPING:
        if not h.is_url(constants.TYPE_MAPPING[type]):
            return read_schema(constants.TYPE_MAPPING[type])
        else:
            # TODO better manage error conditions with appropriate http code and message
            return json.loads(requests.get(constants.TYPE_MAPPING[type]).content)
    else:
        raise InvalidURL(_(("Type {} not found into available mappings, please check your configuration").format(type)))
    # except Exception as ex:
    #     logging.log(logging.ERROR,str(ex), exc_info=1)
    #     return jsonify(error=str(ex)), 404


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

    def functionLoader(name):
        return template[name]
    env = Environment(
                loader=FunctionLoader(functionLoader),
                # autoescape=select_autoescape(['html', 'xml']),
                autoescape=True,
                #newline_sequence='\r\n',
                trim_blocks=False,
                keep_trailing_newline=True)
    for f in template.keys():
        if f in constants.FIELDS_TO_SKIP:
            continue
        # TODO check python3 compatibility 'unicode' may disappear?
        if isinstance(template[f],(str,unicode)):
            try:
                _template = env.get_template(f)
                template[f] = _template.render(model)
            except TemplateSyntaxError as e:
                raise Exception(_('Unable to interpolate field \'{}\' line \'{}\''.format(f,str(e.lineno))))
            except Exception as e:
                raise Exception(_('Unable to interpolate field \'{}\': {}'.format(f,str(e))))
    ###########################################################################