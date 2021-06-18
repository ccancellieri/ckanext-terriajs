# encoding: utf-8

import logging
import datetime
import time
import json

import ckanext.terriajs.constants as constants

from ckan.common import config
import ckan.common as converters
import six
from six import text_type

import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckan.logic as logic
import ckan.logic.schema as schema_
import ckan.lib.dictization as dictization
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization.model_save as model_save
import ckan.lib.navl.dictization_functions
import ckan.lib.navl.validators as validators
import ckan.lib.plugins as lib_plugins
import ckan.lib.email_notifications as email_notifications
import ckan.lib.search as search
import ckan.lib.uploader as uploader
import ckan.lib.datapreview
import ckan.lib.app_globals as app_globals
import ast

import ckan.plugins.toolkit as toolkit

context = toolkit.c

from ckan.common import _, request

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_get_action = logic.get_action
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust


from flask import Blueprint
from six import text_type

from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h
import re
from paste.deploy.converters import asbool

terriajs = Blueprint(constants.NAME, __name__)

def _override_is_enabled(d, set_to):
    def _override_items(group, set_to):
        for item in _items_of(group):
            if u'type' in item and item[u'type'] == u'group':
                _override_items(item,set_to)
                continue
            item[u'isEnabled'] = set_to

    for group in _catalog_groups(d):
        _override_items(group, set_to)

# def _catalog_groups(terria_config):
#     if u'catalog' in map(unicode.lower, terria_config.keys()):
#         # TODO not case insensitive
#         return terria_config[u'catalog']
#     return []

# def _items_of(group):
#     if u'items' in map(unicode.lower, group.keys()):
#         # TODO not case insensitive
#         return group[u'items']
#     return []

# def terriajs_config_forced(resource_view_id):
#     return json.dumps(_base(resource_view_id, True))

# def terriajs_config(resource_view_id):
#     return json.dumps(_base(resource_view_id))

# terriajs.add_url_rule(u'/terriajs/terriajs_config/force_enabled/<resource_view_id>.json', view_func=terriajs_config_forced, methods=[u'GET'])
# terriajs.add_url_rule(u'/terriajs/terriajs_config/<resource_view_id>.json', view_func=terriajs_config, methods=[u'GET'])

# def config_groups_forced(resource_view_id):
#     terria_config = _base(resource_view_id, True)

#     # returns all the first level items (groups)
#     return json.dumps(_catalog_groups(terria_config))

# def config_groups(resource_view_id):
#     terria_config = _base(resource_view_id)

#     # returns all the first level items (groups)
#     return json.dumps(_catalog_groups(terria_config))

# terriajs.add_url_rule(u'/terriajs/terriajs_config/groups/force_enabled/<resource_view_id>', view_func=config_groups_forced, methods=[u'GET'])
# terriajs.add_url_rule(u'/terriajs/terriajs_config/groups/<resource_view_id>', view_func=config_groups, methods=[u'GET'])


### 
import copy
def _base(resource_view_id, force_enabled=False):

    resource_view = get_action(u'resource_view_show')\
        (None, {u'id': resource_view_id})
    if resource_view is None:
        raise NotFound(_('View was not found.'))
    # return h.dump_json(view.config)

    if u'terriajs_config' not in resource_view:
        return {}

    terria_type = resource_view.get('terriajs_type',constants.DEFAULT_TYPE)

    # TODO _override_is_enabled(terria_config,force_enabled, terria_type)

    if terria_type == constants.DEFAULT_TYPE:
        terria_config = json.loads(resource_view.get('terriajs_config',{}))
    else:
        # terria_config is an item we've to wrap to obtain a valid catalog
        terria_config = copy.deepcopy(constants.TERRIAJS_CONFIG)
        terria_config['catalog'].append(json.loads(resource_view.get('terriajs_config',{})))

    return terria_config

def terriajs_config(resource_view_id):
    return json.dumps(_base(resource_view_id))

terriajs.add_url_rule(u'/terriajs/config/<resource_view_id>.json', view_func=terriajs_config, methods=[u'GET'])





