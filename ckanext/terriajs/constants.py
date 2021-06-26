
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

TYPE_MAPPING = {
#    'smart-csv':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/SmartCsvCatalogItem.json?&alt=media',
#    'csv':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/CsvCatalogItem_type.json?&alt=media',
#    'wms':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/WebMapServiceCatalogItem_type.json?&alt=media',
#    'group':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/CatalogGroup_type.json?&alt=media',
#    'ckan-group':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/CkanCatalogGroup_type.json?&alt=media',
#    'ckan':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/CkanCatalogItem_type.json?&alt=media',
#    'csw-group':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/CswCatalogGroup_type.json?&alt=media',
#    'wms':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/WebMapServiceCatalogItem_type.json?&alt=media',
#    'wms-group':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/WebMapServiceCatalogGroup_type.json?&alt=media',
#    'wmts':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/WebMapTileServiceCatalogItem_type.json?&alt=media',
#    'wmts-group':'https://content-storage.googleapis.com/download/storage/v1/b/fao-maps-terriajs-schema/o/WebMapTileServiceCatalogGroup_type.json?&alt=media',
#    DEFAULT_TYPE:'https://storage.googleapis.com/fao-maps-terriajs-schema/Catalog.json'
}

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