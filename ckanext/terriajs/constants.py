
NAME='terriajs'
PAGE_SIZE = 10
DEFAULT_NAME=('ckanext.terriajs.default.name', 'TerriaJS')
ALWAYS_AVAILABLE=('ckanext.terriajs.always_available', True)
DEFAULT_TITLE=('ckanext.terriajs.default.title', 'TerriaJS view')
ICON=('ckanext.terriajs.icon', 'globe')
TERRIAJS_URL=('ckanext.terriajs.url', 'https://localhost/terriajs')
TERRIAJS_SCHEMA_URL=('ckanext.terriajs.schema.url', 'https://storage.googleapis.com/fao-maps-terriajs-schema/Catalog.json')

DEFAULT_TYPE = 'terriajs'
LAZY_ITEM_TYPE = 'terriajs-view'
LAZY_GROUP_TYPE = 'terriajs-group'

TYPE_MAPPING = {}
FORMATS = TYPE_MAPPING.keys()

TERRIAJS_CONFIG = {
               'catalog':[],
               'homeCamera':{
                  'west':-180,
                  'east':180,
                  'north':90,
                  'south':-90
               }
            }