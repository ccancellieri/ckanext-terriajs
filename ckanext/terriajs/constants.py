
import ckan.plugins.toolkit as toolkit
config = toolkit.config

NAME='terriajs'
PAGE_SIZE = 10
DEFAULT_NAME=config.get('ckanext.terriajs.default.name', 'TerriaJS')

DEFAULT_TITLE=config.get('ckanext.terriajs.default.title', 'TerriaJS view')
ICON=config.get('ckanext.terriajs.icon', 'globe')

# MANDATORY
# TERRIAJS base url to reach terriajs
TERRIAJS_URL=config.get('ckanext.terriajs.url', 'https://localhost/terriajs')

# MANDATORY
TERRIAJS_SCHEMA_URL=config.get('ckanext.terriajs.schema.url', 'https://storage.googleapis.com/fao-maps-terriajs-schema/Catalog.json')

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
DEFAULT_FORMATS =config.get('ckanext.terriajs.default.formats', ['csv','wms'])

# type to use as ckan resource when you would like to be free to write the 'full view' not only an item
# it may match one of the items into 
DEFAULT_TYPE = 'terriajs'

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


TERRIAJS_CONFIG = {
               'catalog':[],
               'homeCamera':{
                  'west':-180,
                  'east':180,
                  'north':90,
                  'south':-90
               }
            }