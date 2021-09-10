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