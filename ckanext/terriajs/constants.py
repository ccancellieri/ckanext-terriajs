from sqlalchemy.sql.expression import true
import ckan.plugins.toolkit as toolkit
config = toolkit.config

NAME='terriajs'
PAGE_SIZE = 10
# DEFAULT_NAME=config.get('ckanext.terriajs.default.name', 'Map')

DEFAULT_TITLE=config.get('ckanext.terriajs.default.title', 'Map')
ICON=config.get('ckanext.terriajs.icon', 'globe')

# MANDATORY
# TERRIAJS base url to reach terriajs
TERRIAJS_URL=config.get('ckanext.terriajs.url', 'https://localhost/terriajs')

# MANDATORY
#TERRIAJS_SCHEMA_URL=config.get('ckanext.terriajs.schema.url', 'https://storage.googleapis.com/fao-maps-terriajs-schema/Catalog.json')

# MANDATORY
# (ref to type-mapping.json)
SCHEMA_TYPE_MAPPING_FILE=config.get('ckanext.terriajs.schema.type_mapping','./type-mapping.json')
# Used internally: to hold the type-mapping file content as a dict
TYPE_MAPPING = {}
# Used internally: Will contain the types defined into the file type-mapping
FORMATS = TYPE_MAPPING.keys()

ALWAYS_AVAILABLE=config.get('ckanext.terriajs.always_available', True)

# List of formats supported for view auto creation (create the view when create the resource)
# TODO note may require extensions to support other formats at the b.e.
# TODO wmts incoming...
DEFAULT_FORMATS =config.get('ckanext.terriajs.default.formats', ['csv','wms','mvt'])

# use this type to define a group into terria hierarchy
# type used to define a group of pointers (to a set of views). (resolved internally) 
LAZY_GROUP_TYPE = 'terriajs-group'

# type used internally to define a pointer to a view. (resolved internally) 
LAZY_ITEM_TYPE = 'terriajs-view'

# synchronize the item terria configuration (lazily) using:
# none: Use the json configuration
# resource: Use title and description of the resource (you are creating a view on top of that)
# dataset: Use name and description of the parent dataset
SYNCH_WITH=['none','resource','dataset']

import os
path = os.path

PATH_ROOT=path.realpath(path.join(path.dirname(__file__),'..'))
# 
PATH_SCHEMA=path.realpath(config.get('ckanext.terriajs.path.schema', path.join(PATH_ROOT,'schema')))
# Used as jinja template to initialize the items values, it's name is by convention the type
# same type may also be located under mapping
PATH_TEMPLATE=path.realpath(config.get('ckanext.terriajs.path.template', path.join(PATH_ROOT,'template')))

# type to use as ckan resource when you would like to be free to write the 'full view' not only an item
# it may match one of the items into 
DEFAULT_TYPE = 'terriajs-catalog'

import json
import ckanext.terriajs.utils as utils
TERRIAJS_CATALOG = utils._json_load(PATH_TEMPLATE,'{}.json'.format(DEFAULT_TYPE))
if not TERRIAJS_CATALOG:
   raise Exception('Unable to locate {} template into the template folder ({})'.format(DEFAULT_TYPE,PATH_TEMPLATE))

# type used to define a group of pointers (to a set of views). (resolved internally) 
# TODO: filename is binded with the TYPE value!!!
# LAZY_GROUP_SCHEMA = json.loads(utils.json_load(PATH_SCHEMA,''.join([LAZY_GROUP_TYPE, '.json'])))
# if not LAZY_GROUP_SCHEMA:
#    raise Exception('Unable to locate {} template into the template folder ({})'.format(LAZY_GROUP_TYPE,PATH_SCHEMA))

# type used internally to define a pointer to a view. (resolved internally) 
# TODO: filename is binded with the TYPE value!!!
# LAZY_ITEM_SCHEMA = json.loads(utils.json_load(PATH_SCHEMA,''.join([LAZY_ITEM_TYPE, '.json'])))
# if not LAZY_ITEM_SCHEMA:
#    raise Exception('Unable to locate {} template into the template folder ({})'.format(LAZY_ITEM_TYPE,PATH_SCHEMA))


# fields to do not interpolate with jinja2 (f.e. they are a template of other type)
FIELDS_TO_SKIP={'featureInfoTemplate':true}

# REST paths
REST_MAPPING_PATH='/terriajs/mapping/'
REST_SCHEMA_PATH='/terriajs/schema/'
