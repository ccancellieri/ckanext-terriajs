# from sqlalchemy.sql.expression import true
import ckan.plugins.toolkit as toolkit
config = toolkit.config
import json
import os
path = os.path
PATH_ROOT=path.realpath(path.join(path.dirname(__file__),'..'))

# (Internal)
# this indicate the type of the view stored into the DB
TYPE='terriajs'

# (Optional)
DEFAULT_TITLE=config.get('ckanext.terriajs.default.title', 'Map')
ICON=config.get('ckanext.terriajs.icon', 'globe')

# MANDATORY
# TERRIAJS base url to reach terriajs
TERRIAJS_URL=config.get('ckanext.terriajs.url', 'https://localhost/terriajs')

# MANDATORY
# (ref to type-mapping.json)
SCHEMA_TYPE_MAPPING_FILE=config.get('ckanext.terriajs.schema.type_mapping','./type-mapping.json')

# (Optional)
# fields to do not interpolate with jinja2 (f.e. they are a template of other type)
FIELDS_TO_SKIP = config.get('ckanext.terriajs.skip.fields', ['featureInfoTemplate'])

# (Optional)
# this flag will prevent resource_view_clear action if enabled. (True by Default)
PREVENT_CLEAR_ALL=config.get('ckanext.terriajs.prevent_clear_all', True)

# (Optional)
# Can cause problems with missing mapped types.
ALWAYS_AVAILABLE = config.get('ckanext.terriajs.always_available', True)

# (Optional)
# List of formats supported for view auto creation (create the view when create the resource)
# NOTE may require extensions to support other formats at the b.e.
# in case you want to override/customize it should be a json array like:
# ckanext.terriajs.default.formats=["csv","wms","mvt","test"]
DEFAULT_FORMATS = config.get('ckanext.terriajs.default.formats', ['csv','wms','mvt'])
if isinstance(DEFAULT_FORMATS,str):
   # log.debug("DEFAULT_FORMATS is still a string: {}".format(PATH_SCHEMA))
   DEFAULT_FORMATS = json.loads(DEFAULT_FORMATS)
if not isinstance(DEFAULT_FORMATS,list):
   raise Exception('DEFAULT_FORMATS should be an array of valid format strings')

# (Optional)
# SERVER LOCAL PATH FOLDER WHERE JSON-SCHEMA are located.
PATH_SCHEMA=path.realpath(config.get('ckanext.terriajs.path.schema', path.join(PATH_ROOT,'schema')))

# (Optional)
# Used as jinja template to initialize the items values, it's name is by convention the type
# same type may also be located under mapping
PATH_TEMPLATE=path.realpath(config.get('ckanext.terriajs.path.template', path.join(PATH_ROOT,'template')))

# (Internal)
# use this type to define a group into terria hierarchy
# type used to define a group of pointers (to a set of views). (resolved internally)
LAZY_GROUP_TYPE = 'terriajs-group'

# (Internal)
# type used internally to define a pointer to a view. (resolved internally)
LAZY_ITEM_TYPE = 'terriajs-view'

# (Internal)
# type to use as ckan resource when you would like to be free to write the 'full view' not only an item
# it may match one of the items into 
CATALOG_TYPE = 'terriajs-catalog'

# REST paths
REST_MAPPING_PATH='/{}/mapping'.format(TYPE)
REST_SCHEMA_PATH='/{}/schema'.format(TYPE)
# TODO REST_*_PATH
# document PAGE_SIZE
PAGE_SIZE = 15

##############################
# (Internal)
# VIEW SCHEMA MODEL
# NOTE the actual values below are also affecting
# queries and js, think twice before you change them 
TERRIAJS_CONFIG_KEY='terriajs_config'
TERRIAJS_TYPE_KEY='terriajs_type'
TERRIAJS_SCHEMA_KEY='terriajs_schema'
TERRIAJS_URL_KEY='terriajs_url'

##############################
# Initialized at config time

# (Internal)
# to hold the type-mapping file content as a dict
TYPE_MAPPING = {}
# (Internal)
#  Will contain the types defined into the file type-mapping
FORMATS = {}
# (Internal)
#  Will contain the schema and template defined with the type-mapping
JSON_CATALOG = {}

