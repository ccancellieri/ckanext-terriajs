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

def config_disabled(resource_view_id):
    return json.dumps(_base(resource_view_id, force=True, force_to=False))

def config_enabled(resource_view_id):
    return json.dumps(_base(resource_view_id, force=True, force_to=True))
    
def config(resource_view_id):
    return json.dumps(_base(resource_view_id, force=False))

terriajs.add_url_rule(u'/terriajs/config/enabled/<resource_view_id>.json', view_func=config_enabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/disabled/<resource_view_id>.json', view_func=config_disabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/<resource_view_id>.json', view_func=config, methods=[u'GET'])

### 
import copy
def _base(resource_view_id, force=False, force_to=False):

    view_config = _get_config(resource_view_id)
    # TODO _override_is_enabled(terria_config,f_get_vieworce_enabled, terria_type)

    if type == constants.DEFAULT_TYPE:
        # it's default type, let's leave it as it is (raw)
        config = view_config['config']
    else:
        # terria_config is an item we've to wrap to obtain a valid catalog
        config = copy.deepcopy(constants.TERRIAJS_CONFIG)
        config['catalog'].append(_resolve(view_config['config'], force, force_to))
        config.update({'homeCamera':view_config['camera']})

    return config


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
from ckan.model.group import Group

import sqlalchemy as sa
from ckan.model import types as _types
def query_view_by_type():
    '''Returns the count of ResourceView not in the view types list'''
    return meta.Session.query(
                    ResourceView.id,
                    Group.title.label('organization_title'),
                    Package.title.label('dataset_title'),
                    Package.notes.label('dataset_description'),
                    Resource.name.label('resource_name'),
                    Resource.description.label('resource_description'),
                    ResourceView.config
                ).filter(Package.id == Resource.package_id)\
                .filter(ResourceView.resource_id == Resource.id)\
                .filter(Package.owner_org == Group.id)\
                .filter(ResourceView.view_type == constants.NAME)

from sqlalchemy import or_, and_, not_

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
                # Skip DEFAULT_TYPE (full config)
                #.and_(not_(ResourceView.config.like('%\'terriajs_type\': \'{}\'%'.format(constants.DEFAULT_TYPE)))))

    views = existing_views.order_by(Resource.name)

    page = args.get('page', 0, type=int)
    start=page*constants.PAGE_SIZE
    return json.dumps(views.slice(start, start+constants.PAGE_SIZE).all())
    # return views


def _get_view_details():

    args = request.args
    
    _view_id = args.get('view_id', None, type=str)
    
    view=meta.Session.query(
                    ResourceView.id,
                    Group.title.label('organization_title'),
                    Package.title.label('dataset_title'),
                    Package.notes.label('dataset_description'),
                    Resource.name.label('resource_name'),
                    Resource.description.label('resource_description'),
                    ResourceView.config
                ).filter(ResourceView.id == _view_id)\
                .filter(Package.owner_org == Group.id)\
                .filter(Package.id == Resource.package_id)\
                .filter(ResourceView.resource_id == Resource.id)
    return json.dumps(view.one())

terriajs.add_url_rule(u'/terriajs/describe', view_func=_get_view_details, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/search', view_func=_get_list_of_views, methods=[u'GET'])



def _resolve(item, force=False, force_to=False):
    '''resolve from LAZY_GROUP_TYPE to terriajs native format\
        cherry picking the view by ID from all the available metadata views'''
    
    type = item and item.get('type',None)
    if not type:
        #TODO LOG WARN
        return item
    
    elif type== constants.LAZY_ITEM_TYPE:
        # let's resolve the view by id
        try:
            view_config = _get_config(item.get('id',None))
            
            # is it a nested lazy load item, let's try to resolve again
            item.update(_resolve(view_config['config'], force, force_to))
            
        except Exception as e:
            #TODO LOG (skipping unrecognized object)
            pass

    elif type == constants.LAZY_GROUP_TYPE:
        item.update({u'type':u'group'})


    if force and item.get('type', None) != 'group':
        item['isEnabled'] = force_to
    else:
        items = item.get('items',None)
        if items:
            for _item in items:
                _resolve(_item, force, force_to)
    
    return item

def _get_view(view_id):
    return view_id and query_view_by_type().filter(ResourceView.id==view_id).one()

def _get_config(view_id):

    view = view_id and _get_view(view_id)
    if not view:
        raise Exception(_('No view found for view_id: ')+str(view_id))

    view_config = view.config

    config = view_config and json.loads(view_config.get('terriajs_config',None))
    if not config:
        raise Exception(_('No config found for view: ')+str(view_id))

    type = view_config and view_config.get('terriajs_type',None)
    if not type:
        raise Exception(_('No type found for view: ')+str(view_id))
    
    synch=view_config.get('terriajs_synch','none')
    if synch != 'none':
        if synch == 'resource':
            config['name']=view.resource_name or config['name']
            config['description']=view.resource_description or config['description']
        elif synch == 'dataset':
            config['name']=view.dataset_title or config['name']
            config['description']=view.dataset_description or config['description']
        else:
            raise Exception(_("Unsupported synch mode: ")+str(synch))
    
    camera={
        'east':view_config.get('east',180),
        'west':view_config.get('west',-180),
        'north':view_config.get('north',90),
        'south':view_config.get('south',-90)
    }
    
    return { 'config':config, 'type':type, 'synch':synch, 'camera':camera }