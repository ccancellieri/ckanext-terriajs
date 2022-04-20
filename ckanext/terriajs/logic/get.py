# encoding: utf-8

import json

import ckan.lib.helpers as h
import ckan.logic as logic
import ckanext.jsonschema.logic.get as _g
import ckanext.jsonschema.view_tools as _vt
from ckan.common import _, json
from ckan.plugins.toolkit import request
from flask import redirect
from six import PY3, text_type

# Define some shortcuts
NotFound = logic.NotFound
ValidationError = logic.ValidationError

import logging

import ckanext.terriajs.constants as constants
import ckanext.terriajs.logic.query as query

log = logging.getLogger(__name__)

from flask import Blueprint, jsonify

terriajs = Blueprint(constants.TYPE, __name__)

def item_disabled(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')

    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=False,
        force=True,
        force_to=False,
        _external=True
    ))

def item_enabled(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')


    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=False,
        force=True,
        force_to=True,
        _external=True
    ))

def item(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')


    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=False,
        force=False,
        _external=True
    ))

terriajs.add_url_rule('/{}/item/<resource_view_id>.json'.format(constants.TYPE), view_func=item, methods=[u'GET'])

terriajs.add_url_rule('/{}/item/disabled/<resource_view_id>.json'.format(constants.TYPE), view_func=item_disabled, methods=[u'GET'])

terriajs.add_url_rule('/{}/item/enabled/<resource_view_id>.json'.format(constants.TYPE), view_func=item_enabled, methods=[u'GET'])

def config_disabled(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')


    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=True,
        force=True,
        force_to=False,
        _external=True
    ))

def config_enabled(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')


    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=True,
        force=True,
        force_to=True,
        _external=True
    ))


def _config(resource_view_id):
    # Shortcut for retrocompatibility
    # TODO: remove all of these endpoints and use those of the framework
    view = _g.get_view(resource_view_id)
    package_id = view.get('package_id')
    resource_id = view.get('resource_id')

    return redirect(h.url_for(    
        'jsonschema.get_view_body', 
        package_id=package_id,
        resource_id=resource_id,
        view_id=resource_view_id,
        resolve=True,
        wrap=True,
        force=False,
        _external=True
    ))

# TODO unify/parametrize
terriajs.add_url_rule('/{}/config/enabled/<resource_view_id>.json'.format(constants.TYPE), view_func=config_enabled, methods=[u'GET'])
terriajs.add_url_rule('/{}/config/disabled/<resource_view_id>.json'.format(constants.TYPE), view_func=config_disabled, methods=[u'GET'])
terriajs.add_url_rule('/{}/config/<resource_view_id>.json'.format(constants.TYPE), endpoint='config', view_func=_config, methods=[u'GET'])

### 
#import copy


# def _base(resource_view_id, force=False, force_to=False, itemOnly=False):

#     view_config = _get_config(resource_view_id)

#     # if type == constants.DEFAULT_TYPE:
#     #     # it's default type, let's leave it as it is (raw)
#     #     _config = view_config['config']
#     if itemOnly:
#         # do not wrap the item with a valid terria configuration
#         _config = _resolve(view_config['config'], force, force_to)
#     else:
#         # terria_config is an item we've to wrap to obtain a valid catalog        
        
#         # TODO: This is because we don't have a proper registration of terriajs items into the registry
#         # Replace with get_template_of
        
#         _config = copy.deepcopy(_c.JSON_CATALOG[_c.JSON_TEMPLATE_KEY].get(os.path.join(constants.TYPE, constants.CATALOG_TYPE) + '.json'))
        
#         #_config = copy.deepcopy(_t.get_template_of(constants.CATALOG_TYPE))
#         _config['catalog'].append(_resolve(view_config['config'], force, force_to))
#         _config.update({'homeCamera':view_config['camera']})

#     return _config

def resolve(item, force, force_to):

    try:
        return _resolve(item, force, force_to)
    except:
        error_message = "Error during resolving: {}".format(item)
        log.error(error_message)
        log.error("force: {}, force_to:{}".format(force, force_to))
        
        return {
            "id": "",
            "description": error_message,
            "type": "group"
        }


def _resolve(item, force=False, force_to=False):
    '''resolve from LAZY_GROUP_TYPE to terriajs native format\
        cherry picking the view by ID from all the available metadata views'''
    
    catalog = item.get('catalog')
    if catalog and isinstance(catalog, list):
        for catalog_item in catalog:
            catalog_item = resolve(catalog_item, force, force_to)
        return item

    type = item and item.get('type')
    if not type:
        #TODO LOG WARN
        return item
    
    elif type == constants.LAZY_ITEM_TYPE:
        # let's resolve the view by id
        view = _g.get_view(item.get('id'))
        model = _vt.get_model(view.get('package_id'), view.get('resource_id'))
        view_body = _vt.get_view_body(view)
        _terriajs_config = _vt.interpolate_fields(model, view_body)     
        
        if not _terriajs_config:
            raise Exception(_('Unable to resolve view id: {}'.format(item.get('id'))))

        # is it a nested lazy load item, let's try to resolve again
        item.update(resolve(_terriajs_config, force, force_to))

    elif type == constants.LAZY_GROUP_TYPE:
        item.update({u'type':u'group'})


    if force and item.get('type') != 'group':
        item['isEnabled'] = force_to
    else:
        items = item.get('items')
        if items:
            for _item in items:
                _item.update(resolve(_item, force, force_to))
    
    return item

# def _get_config(view_id):

#     # the result is different
#     #view = view_id and query.view_by_id(view_id)
#     view = _g.get_view(view_id)
#     if not view:
#         raise Exception(_('No view found for view_id: {}'.format(str(view_id))))

#     # view_config = view.get('config',None)
#     # if not view_config:
#     #     raise Exception(_('Unable to find a valid configuration for view ID: {}'.format(str(view_id))))

#     # jsonschema_type = view_config and view_config.get(_c.SCHEMA_TYPE_KEY ,None)
#     # if not jsonschema_type:
#     #     raise Exception(_('No type found for view: {}'.format(str(view_id))))

#     model = _get_model(dataset_id=get_or_bust(view,'package_id'),resource_id=get_or_bust(view,'resource_id'))
#     # terriajs_config = get_or_bust(view_config, _c.SCHEMA_OPT_KEY)
    
#     # backward compatibility (the string is now stored as dict)
#     # if not isinstance(terriajs_config,dict):
#     #     terriajs_config = json.loads(terriajs_config)

#     # Interpolation
#     view_type = view.get("view_type") 
#     view_opts = _vt.get_view_opt(view)
#     view_jsonschema_type = _vt.get_view_type(view)
#     view_body = _vt.get_view_body(view)

#     _terriajs_config = _vt.interpolate_fields(model, view_body)     

#     camera={
#         'east': view_opts.get('east',180),
#         'west': view_opts.get('west',-180),
#         'north': view_opts.get('north',90),
#         'south': view_opts.get('south',-90)
#     }
#     return { 'config': _terriajs_config, 'type': view_jsonschema_type, 'camera':camera }

# def _get_model(dataset_id, resource_id):
#     '''
#     Returns the model used by jinja2 template
#     '''

#     if not dataset_id or not resource_id:
#         raise Exception('wrong parameters we expect a dataset_id and a resource_id')

#     # TODO can we have a context instead of None?
#     pkg = toolkit.get_action('package_show')(None, {'id':dataset_id})
#     if not pkg:
#         raise Exception('Unable to find dataset, check input params')

#     pkg = _t.dictize_pkg(pkg)


#     # res = filter(lambda r: r['id'] == view.resource_id,pkg['resources'])[0]
#     res = next(r for r in pkg['resources'] if r['id'] == resource_id)
#     if not res:
#         raise Exception('Unable to find resource under this dataset, check input params')

#     organization_id = pkg.get('owner_org')

#     # return the model as dict
#     _dict = {
#         'package':pkg,
#         'organization': toolkit.get_action('organization_show')(None, {'id': organization_id}),
#         'resource':res,
#         'ckan':{'base_url':h.url_for('/', _external=True)},
#         'terriajs':{'base_url':constants.TERRIAJS_URL} # TODO replace with opt.base_url?? 
#         }

#     return _dict 
    
def _encode_str(value):
    if PY3 and isinstance(value, text_type):
        value = str(value)
    elif (not PY3) and isinstance(value, unicode):
        value = value.encode("utf-8")
    
    return value


def _model(dataset_id, resource_id):
    '''
    Useful to the UI to serialize the model to understand and better write jinja2 templates
    '''
    try:    
        # args = request.args
        # dataset_id = args.get('dataset_id', None, type=str)
        # resource_id = args.get('resource_id', None, type=str)
        return json.dumps(_vt.get_model(dataset_id,resource_id))
    except Exception as ex:
        error=_("Unable to get model: {}".format(str(ex)))
        logging.log(logging.ERROR,error)
        return jsonify(error), 404

terriajs.add_url_rule('{}/<dataset_id>/<resource_id>'.format(constants.REST_MAPPING_PATH), endpoint='model', view_func=_model, methods=[u'GET'])

########################################

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

terriajs.add_url_rule('/{}/search'.format(constants.TYPE), view_func=_get_list_of_views, methods=[u'GET'])

########################################

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
terriajs.add_url_rule('/{}/describe'.format(constants.TYPE), view_func=_get_view_details, methods=[u'GET'])
