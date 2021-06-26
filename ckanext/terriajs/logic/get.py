# encoding: utf-8

import logging
import datetime
import time
import json
from requests.exceptions import InvalidSchema

from requests.models import InvalidURL

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

def _catalog_groups(terria_config):
    if u'catalog' in map(unicode.lower, terria_config.keys()):
        # TODO not case insensitive
        return terria_config[u'catalog']
    return []

def _items_of(group):
    if u'items' in map(unicode.lower, group.keys()):
        # TODO not case insensitive
        return group[u'items']
    return []

def terriajs_config_forced(resource_view_id):
    return json.dumps(_base(resource_view_id, True))


terriajs.add_url_rule(u'/terriajs/config/force_enabled/<resource_view_id>.json', view_func=terriajs_config_forced, methods=[u'GET'])


def config_groups_forced(resource_view_id):
    terria_config = _base(resource_view_id, True)

    # returns all the first level items (groups)
    return json.dumps(_catalog_groups(terria_config))

def config_groups(resource_view_id):
    terria_config = _base(resource_view_id)

    # returns all the first level items (groups)
    return json.dumps(_catalog_groups(terria_config))

terriajs.add_url_rule(u'/terriajs/config/groups/force_enabled/<resource_view_id>', view_func=config_groups_forced, methods=[u'GET'])
terriajs.add_url_rule(u'/terriajs/config/groups/<resource_view_id>', view_func=config_groups, methods=[u'GET'])


### 
import copy
def _base(resource_view_id, resolve=True, force_enabled=False):

    #TODO checkme
    resource_view = _get_action(u'resource_view_show')(None, {u'id': resource_view_id})
    if resource_view is None:
        raise NotFound(_('View was not found.'))

    # terria_config, terria_type = _get_config(resource_view_id)
    
    # if not config:
    #     raise InvalidSchema(_('No config found for view: ')+str(resource_view_id))
    
    terria_type = resource_view.get('terriajs_type',constants.DEFAULT_TYPE)
    
    # TODO _override_is_enabled(terria_config,force_enabled, terria_type)
    
    terria_config = json.loads(resource_view.get('terriajs_config',{}))
    
    if terria_type != constants.DEFAULT_TYPE:
        # terria_config is an item we've to wrap to obtain a valid catalog
        config = copy.deepcopy(constants.TERRIAJS_CONFIG)
    
    if resolve:
        config['catalog'].append(_resolve(terria_config))
    else:
        config['catalog'].append(terria_config) 

    return config

def config(resource_view_id):
    return json.dumps(_base(resource_view_id)).decode('string_escape')

terriajs.add_url_rule(u'/terriajs/config/<resource_view_id>.json', view_func=config, methods=[u'GET'])

# TODO better manage error conditions with appropriate http code and message
import requests
import os
schema_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../schema/'))
def mapping(type):
    '''
    provides a proxy for local or remote url based on schema-mapping.json file and passed <type> param
    '''
    if type in constants.TYPE_MAPPING:
        if not h.is_url(constants.TYPE_MAPPING[type]):
            with open(schema_path+'/'+constants.TYPE_MAPPING[type]) as s:
                return json.dumps(json.load(s))
        else:
            return requests.get(constants.TYPE_MAPPING[type]).content
    else:
        raise InvalidURL(_("Type "+type+" not found into available mappings, please check your configuration"))

terriajs.add_url_rule(u'/terriajs/mapping/<type>', view_func=mapping, methods=[u'GET'])

from ckan.model import meta
from ckan.model.resource_view import ResourceView
from ckan.model.resource import Resource
from ckan.model.package import Package

import sqlalchemy as sa
from ckan.model import types as _types
def query_view_by_type():
    '''Returns the count of ResourceView not in the view types list'''
    return meta.Session.query(
                    ResourceView.id,
                    Package.title.label('dataset_title'),
                    Package.notes.label('dataset_description'),
                    Resource.name.label('resource_name'),
                    Resource.description.label('resource_description'),
                    ResourceView.config
                ).filter(Package.id == Resource.package_id)\
                .filter(ResourceView.resource_id == Resource.id)\
                .filter(ResourceView.view_type == constants.NAME)

from sqlalchemy import or_




def _get_list_of_views():
    
    # Set the pagination configuration
    args = request.args
    
    _dataset_title = args.get('dataset_title', None, type=str)
    _dataset_title = _dataset_title and '%{}%'.format(_dataset_title)

    _dataset_description = args.get('dataset_description', None, type=str)
    _dataset_description = _dataset_description and '%{}%'.format(_dataset_description)

    _resource_name = args.get('resource_name', None, type=str)
    _resource_name = _resource_name and '%{}%'.format(_resource_name)

    existing_views=query_view_by_type()\
        .filter(or_(_resource_name and Resource.name.like(_resource_name),
                    _dataset_title and Package.title.like(_dataset_title),
                    _dataset_description and Package.notes.like(_dataset_description)))
    
    views = existing_views.order_by(Resource.name)

    page = args.get('page', 0, type=int)
    start=page*constants.PAGE_SIZE

    views.slice(start, start+constants.PAGE_SIZE)
    return json.dumps(views.all())
    # return views


terriajs.add_url_rule(u'/terriajs/search', view_func=_get_list_of_views, methods=[u'GET'])

def _get_view(id_view):
    return id_view and query_view_by_type().filter(ResourceView.id==id_view).one()

def _get_config(id_view):    
    view = _get_view(id_view)
    if not view:
        raise InvalidSchema(_('View not found for item id: ')+str(id_view))
    view_config=view.config

    config = view_config and json.loads(view_config.get('terriajs_config',None))
    if not config:
        raise InvalidSchema(_('No config found for view: ')+str(view))

    type = view_config and view_config.get('terriajs_type',None)
    if not type:
        raise InvalidSchema(_('No type found for view: ')+str(view))
    
    # return config.decode('string_escape'), type
    return config, type

def _resolve(item):
    '''resolve from LAZY_GROUP_TYPE to terriajs native format\
        cherry picking the view by ID from all the available metadata views'''

    type = item and item.get('type',None)
    if not type:
        #TODO LOG WARN
        return item

    elif type==constants.LAZY_ITEM_TYPE:
        # let's resolve the view by id
        try:
            config, type = _get_config(item.get('id',None))
            item.update(config)
        except Exception as e:
            #TODO LOG (skipping unrecognized object)
            pass

    elif type ==constants.LAZY_GROUP_TYPE:
        item.update({u'type':u'group'})

    items = item.get('items',None)
    if items:
        for _item in items:
            _resolve(_item)

    return item

def navigate(root_view_id):

    config = _get_config(root_view_id)
    if not config:
        raise InvalidSchema(_('No config found for view: ')+str(config))
    
    _resolve(config)

    return json.dumps(config).decode('string_escape')

terriajs.add_url_rule(u'/terriajs/navigate/<root_view_id>.json', view_func=navigate, methods=[u'GET'])

