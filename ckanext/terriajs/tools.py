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



def resolve_mapping(type):
    '''
    try to resolve the url from the schema-mapping configuration.
    return an url
    '''
    if type in constants.TYPE_MAPPING:
        if not h.is_url(constants.TYPE_MAPPING[type]):
            return h.url_for(constants.MAPPING_PATH+str(type), _external=True)
        else:
            return constants.TYPE_MAPPING[type]
    else:
        error = "Type "+type+" not found into available mappings, please check your configuration"
        logging.log(logging.ERROR,error)
        raise InvalidURL(_(error))


# TODO DOCUMENT (Default mapping)
def get_view_type(resource):
    resource_type = resource.get('format','').lower()
    # type has been configured, is it matching into the config?
    if resource_type not in constants.TYPE_MAPPING.keys():
        resource_type = constants.DEFAULT_TYPE
    
    return resource_type

def get_config(resource):
    
    # generate base configuration
    terriajs_config= None
    resource_type = get_view_type(resource)

    if resource_type == constants.DEFAULT_TYPE:
        return constants.TERRIAJS_CATALOG
    else:
        # USING template mechanism
        terriajs_config = utils.json_load(constants.PATH_TEMPLATE,''.join([resource_type, '.json']))
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