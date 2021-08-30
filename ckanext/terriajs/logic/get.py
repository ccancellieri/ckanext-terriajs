# encoding: utf-8

from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h, get_or_bust
import re
from paste.deploy.converters import asbool
import json
from requests.models import InvalidURL

from ckan.common import config
import ckan.common as converters
# import six
# from six import text_type

import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import _, request

# Define some shortcuts
NotFound = logic.NotFound
ValidationError = logic.ValidationError

import ckanext.terriajs.constants as constants
import logging, traceback
log = logging.getLogger(__name__)

from flask import Blueprint, abort, jsonify
terriajs = Blueprint(constants.NAME, __name__)

def item_disabled(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=True, force_to=False, itemOnly=True))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

def item_enabled(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=True, force_to=True, itemOnly=True))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

def item(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=False, itemOnly=True))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

terriajs.add_url_rule(u'/terriajs/item/<resource_view_id>.json', view_func=item, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/item/disabled/<resource_view_id>.json', view_func=item_disabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/item/enabled/<resource_view_id>.json', view_func=item_enabled, methods=[u'GET'])

def config_disabled(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=True, force_to=False))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

def config_enabled(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=True, force_to=True))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500


def config(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=False))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

terriajs.add_url_rule(u'/terriajs/config/enabled/<resource_view_id>.json', view_func=config_enabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/disabled/<resource_view_id>.json', view_func=config_disabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/<resource_view_id>.json', view_func=config, methods=[u'GET'])

### 
import copy
def _base(resource_view_id, force=False, force_to=False, itemOnly=False):

    view_config = _get_config(resource_view_id)

    if type == constants.DEFAULT_TYPE:
        # it's default type, let's leave it as it is (raw)
        config = view_config['config']
    elif itemOnly:
        # do not wrap the item with a valid terria configuration
        config = _resolve(view_config['config'], force, force_to)
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
    try:
        if type in constants.TYPE_MAPPING:
            if not h.is_url(constants.TYPE_MAPPING[type]):
                with open(schema_path+'/'+constants.TYPE_MAPPING[type]) as s:
                    return json.dumps(json.load(s))
            else:
                return requests.get(constants.TYPE_MAPPING[type]).content
        else:
            raise InvalidURL(_("Type "+type+" not found into available mappings, please check your configuration"))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 404

terriajs.add_url_rule(u'/terriajs/mapping/<type>', view_func=mapping, methods=[u'GET'])

def _resolve(item, force=False, force_to=False):
    '''resolve from LAZY_GROUP_TYPE to terriajs native format\
        cherry picking the view by ID from all the available metadata views'''
    
    type = item and item.get('type',None)
    if not type:
        #TODO LOG WARN
        return item
    
    elif type== constants.LAZY_ITEM_TYPE:
        # let's resolve the view by id
        view_config = _get_config(item.get('id',None))
        
        if not view_config:
            raise Exception(_('Unable to resolve view id: {}'.format(item.get('id',None))))

        # is it a nested lazy load item, let's try to resolve again
        item.update(_resolve(view_config['config'], force, force_to))
            

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

from jinja2 import Template

def _get_config(view_id):

    view = view_id and query.view_by_id(view_id)
    if not view:
        raise Exception(_('No view found for view_id: ')+str(view_id))

    view_config = view.get('config',None)
    if not view_config:
        raise Exception('Unable to find a valid configuration for view ID: '+str(view_id))

    ###########################################################################
    # Jinja2 template
    ###########################################################################
    # TODO can we have a context instead of None?
    pkg = toolkit.get_action('package_show')(None, {'id':get_or_bust(view,'package_id')})
    res = next(r for r in pkg['resources'] if r['id'] == get_or_bust(view,'resource_id'))
    # res = filter(lambda r: r['id'] == view.resource_id,pkg['resources'])[0]
    model = {
        'dataset':pkg,
        'organization': get_or_bust(pkg,'organization'),
        'resource':res,
        'ckan':{'base_url':h.url_for('/', _external=True)},
        'terriajs':{'base_url':constants.TERRIAJS_URL}
        }

    template = view_config and Template(get_or_bust(view_config,'terriajs_config'))
    config = template and template.render(model)

    config = view_config and json.loads(config)
    if not config:
        raise Exception(_('No config found for view: ')+str(view_id))

    # for f in config.keys():
    #     template = Template(config[f])
    #     config[f] = template.render(model)

    ###########################################################################

    type = view_config and view_config.get('terriajs_type',None)
    if not type:
        raise Exception(_('No type found for view: ')+str(view_id))
    
    camera={
        'east':view_config.get('east',180),
        'west':view_config.get('west',-180),
        'north':view_config.get('north',90),
        'south':view_config.get('south',-90)
    }
    return { 'config':config, 'type':type, 'camera':camera }


import query

def _get_list_of_views():
    try:
        # Set the pagination configuration
        args = request.args
        
        _dataset_title = args.get('dataset_title', None, type=str)
        _dataset_title = _dataset_title and '%{}%'.format(_dataset_title)

        _dataset_description = args.get('dataset_description', None, type=str)
        _dataset_description = _dataset_description and '%{}%'.format(_dataset_description)

        _resource_name = args.get('resource_name', None, type=str)
        _resource_name = _resource_name and '%{}%'.format(_resource_name)

        views = query.views_list_query(_dataset_title,_dataset_description,_resource_name)

        page = args.get('page', 0, type=int)
        start=page*constants.PAGE_SIZE
        return json.dumps([u._asdict() for u in views.slice(start, start+constants.PAGE_SIZE).all()])
        # return views
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 404
        #abort(404)

terriajs.add_url_rule(u'/terriajs/search', view_func=_get_list_of_views, methods=[u'GET'])

def _get_view_details():
    try:    
        args = request.args
        
        _view_id = args.get('view_id', None, type=str)
        return json.dumps(query.view_details(_view_id))
    except Exception as ex:
        error=_("Unable to get details for id: {} -> {}".format(_view_id, str(ex)))
        logging.log(logging.ERROR,error)
        return jsonify(error), 404
        #abort(404)


terriajs.add_url_rule(u'/terriajs/describe', view_func=_get_view_details, methods=[u'GET'])