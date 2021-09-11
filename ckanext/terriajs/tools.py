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
def get_view_type(resource):
    resource_type = resource.get('format','').lower()
    # type has been configured, is it matching into the config?
    if resource_type not in constants.TYPE_MAPPING.keys():
        resource_type = constants.DEFAULT_TYPE
    
    return resource_type
    
    return resource_type

def get_config(resource):
    
    resource_type = get_view_type(resource)

    # generate base configuration
    # TODO create and use template mapping
    terriajs_config = read_template('{}.json'.format(resource_type))
    if terriajs_config:
        return terriajs_config
    else:
        # fallback, no template has been found
        return {
            'name': resource.get('name',''),
            'url': resource.get('url',''),
            'description': resource.get('description',''),
            'id': resource.get('id',''),
            'type': resource_type or ''
        }


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


from jinja2.environment import Environment
from jinja2.loaders import FunctionLoader
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
            _template = env.get_template(f)
            template[f] = _template.render(model)
    ###########################################################################