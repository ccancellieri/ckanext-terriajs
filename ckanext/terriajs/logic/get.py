# encoding: utf-8

from jinja2.environment import Environment
from jinja2.loaders import FunctionLoader
# from jinja2.utils import select_autoescape
from ckan.common import json
from ckan.plugins.toolkit import get_action, request, h, get_or_bust
import json
from requests.models import InvalidURL

# import ckan.common as converters
# from paste.deploy.converters import asbool

import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import _, request

# Define some shortcuts
NotFound = logic.NotFound
ValidationError = logic.ValidationError

import ckanext.terriajs.constants as constants
import ckanext.terriajs.logic.query as query
# import ckanext.terriajs.tools as tools
import ckanext.terriajs.utils as utils
import logging
log = logging.getLogger(__name__)

from jinja2 import Template,Markup
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

def _config(resource_view_id):
    try:
        return json.dumps(_base(resource_view_id, force=False))
    except Exception as ex:
        logging.log(logging.ERROR,str(ex), exc_info=1)
        return jsonify(error=str(ex)), 500

terriajs.add_url_rule(u'/terriajs/config/enabled/<resource_view_id>.json', view_func=config_enabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/disabled/<resource_view_id>.json', view_func=config_disabled, methods=[u'GET'])

terriajs.add_url_rule(u'/terriajs/config/<resource_view_id>.json', endpoint='config', view_func=_config, methods=[u'GET'])

### 
import copy
def _base(resource_view_id, force=False, force_to=False, itemOnly=False):

    view_config = _get_config(resource_view_id)

    if type == constants.DEFAULT_TYPE:
        # it's default type, let's leave it as it is (raw)
        _config = view_config['config']
    elif itemOnly:
        # do not wrap the item with a valid terria configuration
        _config = _resolve(view_config['config'], force, force_to)
    else:
        # terria_config is an item we've to wrap to obtain a valid catalog
        _config = copy.deepcopy(constants.TERRIAJS_CATALOG)
        _config['catalog'].append(_resolve(view_config['config'], force, force_to))
        _config.update({'homeCamera':view_config['camera']})

    return _config


# TODO better manage error conditions with appropriate http code and message
import requests

def mapping(type):
    '''
    provides a proxy for local or remote url based on schema-mapping.json file and passed <type> param
    '''
    # try:
    if type in constants.TYPE_MAPPING:
        if not h.is_url(constants.TYPE_MAPPING[type]):
            return _schema(constants.TYPE_MAPPING[type])
        else:
            return requests.get(constants.TYPE_MAPPING[type]).content
    else:
        raise InvalidURL(_(("Type {} not found into available mappings, please check your configuration").format(type)))
    # except Exception as ex:
    #     logging.log(logging.ERROR,str(ex), exc_info=1)
    #     return jsonify(error=str(ex)), 404

terriajs.add_url_rule(''.join([constants.REST_MAPPING_PATH,"<type>"]), view_func=mapping, endpoint='mapping', methods=[u'GET'])

def _schema(name):
    '''
    provides a proxy for local schema definitions
    '''
    # TODO increase security should be/ensure to be under schema_path folder
    return utils.json_load(constants.PATH_SCHEMA, name)

terriajs.add_url_rule(''.join([constants.REST_SCHEMA_PATH,'<name>']), view_func=_schema, endpoint='schema', methods=[u'GET'])

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

def _get_config(view_id):

    view = view_id and query.view_by_id(view_id)
    if not view:
        raise Exception(_('No view found for view_id: {}'.format(str(view_id))))

    view_config = view.get('config',None)
    if not view_config:
        raise Exception(_('Unable to find a valid configuration for view ID: {}'.format(str(view_id))))
    #view_config = json.dumps(view_config)

    ###########################################################################
    # Jinja2 template
    ###########################################################################
    
    model = _get_model(dataset_id=get_or_bust(view,'package_id'),resource_id=get_or_bust(view,'resource_id'))

    # template = view_config and Template(Markup(get_or_bust(view_config,'terriajs_config').decode('string_escape')))
    # config = template and template.render(model)
    # try:
    #     # decode needed for python2.7
    #     config = view_config and json.loads(config)
    #     if not config:
    #         raise Exception(_('No config found for view: {}'.format(str(view_id))
    # except Exception as ex:
    #     raise Exception(_('Unable to parse resulting object should be a valid json:\n {}'.format(str(config),
    #     '\nException: '+str(ex)+
    #     '\nPlease check your template.'))

    _config = json.loads(get_or_bust(view_config,'terriajs_config'))

    def functionLoader(name):
        return _config[name]
    env = Environment(
                loader=FunctionLoader(functionLoader),
                # autoescape=select_autoescape(['html', 'xml']),
                autoescape=True,
                newline_sequence='\r\n',
                trim_blocks=False,
                keep_trailing_newline=True)
    for f in _config.keys():
        # TODO check python3 compatibility 'unicode' may disappear?
        if isinstance(_config[f],(str,unicode)):
            template = env.get_template(f)
            _config[f] = template.render(model)
    ###########################################################################

    type = view_config and view_config.get('terriajs_type',None)
    if not type:
        raise Exception(_('No type found for view: {}'.format(str(view_id))))
    
    camera={
        'east':view_config.get('east',180),
        'west':view_config.get('west',-180),
        'north':view_config.get('north',90),
        'south':view_config.get('south',-90)
    }
    return { 'config':_config, 'type':type, 'camera':camera }

def _get_model(dataset_id, resource_id):
    '''
    Returns the model used by jinja2 template
    '''

    if not dataset_id or not resource_id:
        raise Exception('wrong parameters we expect a dataset_id and a resource_id')

    # TODO can we have a context instead of None?
    pkg = toolkit.get_action('package_show')(None, {'id':dataset_id})
    if not pkg:
        raise Exception('Unable to find dataset, check input params')

    # res = filter(lambda r: r['id'] == view.resource_id,pkg['resources'])[0]
    res = next(r for r in pkg['resources'] if r['id'] == resource_id)
    if not res:
        raise Exception('Unable to find resource under this dataset, check input params')

    # return the model as dict
    return {
        'dataset':pkg,
        'organization': get_or_bust(pkg,'organization'),
        'resource':res,
        'ckan':{'base_url':h.url_for('/', _external=True)},
        'terriajs':{'base_url':constants.TERRIAJS_URL}
        }
    
def _model(dataset_id, resource_id):
    try:    
        # args = request.args
        # dataset_id = args.get('dataset_id', None, type=str)
        # resource_id = args.get('resource_id', None, type=str)
        return json.dumps(_get_model(dataset_id,resource_id))
    except Exception as ex:
        error=_("Unable to get model: {}".format(str(ex)))
        logging.log(logging.ERROR,error)
        return jsonify(error), 404

terriajs.add_url_rule(u'/terriajs/model/<dataset_id>/<resource_id>', endpoint='model', view_func=_model, methods=[u'GET'])

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