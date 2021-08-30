import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
_ = toolkit._
from requests.models import InvalidURL
import json

import ckanext.terriajs.constants as constants
# import ckanext.terriajs.tools
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
            return h.url_for('/terriajs/mapping/'+str(type), _external=True)
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
        terriajs_config = constants.TERRIAJS_CONFIG
    else:
        # package=data_dict.get('package','')
        # terriajs_config = {
        #                 'name': resource.get('name',''),
        #                 'url': resource.get('url',''),
        #                 'description': resource.get('description',''),
        #                 'id': resource.get('id',''),
        #                 'type': resource_type or ''
        #             }
        # USING jinja
        terriajs_config = {
                        'name': '{{resource.name}}',
                        'url': '{{resource.url}}',
                        'description': '{{dataset.notes or resource.description}}',
                        'id': resource.get('id',''),
                        'type': resource_type or ''
                    }

###################################################
# TODO : EXTENSION POINT TO CONFIGURE BASED ON TYPE
###################################################

    if resource_type=='wms':
        terriajs_config.update({'layers': '{{resource.name}}'})
    elif resource_type=='wmts':
        terriajs_config.update({'layer': '{{resource.name}}',
                            "useResourceTemplate": False,
                            "ignoreUnknownTileErrors": True,
                            "treat403AsError": False,
                            "treat404AsError": False,
                            "isLegendVisible": False})

    elif resource_type==constants.LAZY_GROUP_TYPE:
        terriajs_config.update({'items': [], "preserveOrder": True})
    
    # TODO BBOX based on the layer...
    
    return json.dumps(terriajs_config)