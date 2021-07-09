#!/bin/bash

# paster --plugin=ckan config-tool $SRC_DIR/ckan/test-core.ini \
#     "sqlalchemy.url = $TEST_CKAN_SQLALCHEMY_URL" \
#     "ckan.datastore.write_url = $TEST_CKAN_DATASTORE_WRITE_URL" \
#     "ckan.datastore.read_url = $TEST_CKAN_DATASTORE_READ_URL" \
#     "solr_url = $TEST_CKAN_SOLR_URL" \
#     "ckan.redis.url = $TEST_CKAN_REDIS_URL"

# paster --plugin=ckan config-tool $SRC_DIR/ckan/test-core.ini \
paster --plugin=ckan config-tool /srv/app/production.ini \
    "ckanext.terriajs.default.name=TerriaJS" \
    "ckanext.terriajs.always_available=True" \
    "ckanext.terriajs.default.title=TerriaJS view" \
    "ckanext.terriajs.icon=globe" \
    "ckanext.terriajs.url=http://localhost:8080" \
    "ckanext.terriajs.schema.default_type=terriajs" \
    "ckanext.terriajs.schema.type_mapping=$APP_DIR/terriajs-type-mapping.json"

cp ./type-mapping.json $APP_DIR/terriajs-type-mapping.json