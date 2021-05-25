
NAME='terriajs'

DEFAULT_NAME=('ckanext.terriajs.default.name', 'TerriaJS')
ALWAYS_AVAILABLE=('ckanext.terriajs.always_available', True)
DEFAULT_TITLE=('ckanext.terriajs.default.title', 'TerriaJS view')
ICON=('ckanext.terriajs.icon', 'globe')
TERRIAJS_URL=('ckanext.terriajs.url', 'https://localhost/terriajs')
TERRIAJS_SCHEMA_URL=('ckanext.terriajs.schema.url', 'https://storage.googleapis.com/fao-maps-terriajs-schema/Catalog.json')

FORMATS = ['wms','wfs','kml', 'kmz','gjson', 'geojson', 'czml']

TERRIAJS_CONFIG='''{
               "catalog":[
                  {
                     "name":"",
                     "type":"group",
                     "order":1,
                     "description":"",
                     "preserveOrder":true,
                     "items":[]
                  }
               ],
               "homeCamera":{
                  "west":-180,
                  "east":180,
                  "north":90,
                  "south":-90
               }
            }'''