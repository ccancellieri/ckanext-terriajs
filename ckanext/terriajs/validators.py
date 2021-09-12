from sqlalchemy.sql.expression import true
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit

_get_or_bust= toolkit.get_or_bust
_ = toolkit._
# import ckan.logic.validators as v

not_empty = toolkit.get_validator('not_empty')
#ignore_missing = p.toolkit.get_validator('ignore_missing')
#ignore_empty = p.toolkit.get_validator('ignore_empty')
is_boolean = toolkit.get_validator('boolean_validator')
# https://docs.ckan.org/en/2.8/extensions/validators.html#ckan.logic.validators.json_object
# NOT FOUND import ckan.logic.validators.json_object
#json_object = p.toolkit.get_validator('json_object')

import ckan.lib.navl.dictization_functions as df

missing = df.missing
StopOnError = df.StopOnError
Invalid = df.Invalid

import ckanext.terriajs.tools as tools
import ckanext.terriajs.constants as constants
import ckanext.terriajs.logic.get as get
# import ckanext.terriajs.validators as v
import logging
log = logging.getLogger(__name__)

#TODO... something more ckan oriented? (toolkit, etc) dict(?)
def instance_to_dict(i):
    '''
    The Validator receive a resource instance, we need a dict...
    '''
    # TODO try using 
    # context problems
    # import ckan.lib.dictization.model_dictize as model_dictize
    # res = model_dictize.package_dictize(i, toolkit.c)
    # TODO return dict(i)
    resource = {'name': i.name or '',
                'url': i.url or '',
                'description': i.description or '',
                'id': i.id or '',
                'package_id': i.package_id or '',
                'format': (i.format or '')
    }
    if i.url_type == 'upload':
        resource['url'] = h.url_for(
                                    controller='package',
                                    action='resource_download',
                                    id=resource['package_id'],
                                    resource_id=resource['id'],
                                    filename=resource['url'],
                                    qualified=True)
    return resource

def default_type(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    type = data.get(key)
    if not type or type is missing:
        _resource = instance_to_dict(context.get('resource'))
        type = tools.map_resource_to_terriajs_type(_resource)
        if not type:
            errors[key].append(_('Missing default type value, please check available json-mapping formats'))
            raise StopOnError

        data[key] = type


# def default_synch(key, data, errors, context):
#     '''
#     Validator providing default values 
#     '''
#     synch = data.get(key)
#     if not synch or synch is missing:
#         data[key] = 'dataset'

def default_config(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    config = data.get(key)
    if not config or config is missing:
        _resource = instance_to_dict(context.get('resource'))
        # _resource.update({ 'type': _map_resource_format_to_terriajs_type(resource)})
        terriajs_type = tools.map_resource_to_terriajs_type(_resource)
        config = tools.default_template(terriajs_type)
        if not config:
            errors[key].append(_('Missing config value (json body)'))
            raise StopOnError
        data[key] = config

#############################################

import jsonschema
from jsonschema import validate,RefResolver,Draft4Validator,Draft7Validator
import json
import ckan.model as model

_SCHEMA_RESOLVER = jsonschema.RefResolver(base_uri='file://{}/'.format(constants.PATH_SCHEMA), referrer=None)

def _stop_on_error(errors,key,message):
    errors[key].append(_(message))
    raise StopOnError(_(message))

def config_schema_check(key, data, errors, context):
    '''
    Validator providing schema check capabilities
    '''
   # config = json.loads(data[(constants.TERRIAJS_CONFIG_KEY,)])
    config = data.get(key)
    if not config:
        _stop_on_error(errors,key,_('Can\'t validate empty Missing value {}'.format(constants.TERRIAJS_CONFIG_KEY)))

    ##############SIDE EFFECT#################
    # if configuration comes as string:
    # convert incoming string to a dict
    try:
        if not isinstance(config, dict):
            config = data[key] = json.loads(config)
    except Exception as e:
        _stop_on_error(errors,key,'Not a valid json dict :{}'.format(str(e)))
    ##############SIDE EFFECT#################

    terriajs_type = data.get((constants.TERRIAJS_TYPE_KEY,))
    if not terriajs_type or terriajs_type is missing:
        _resource = instance_to_dict(context.get('resource'))
        terriajs_type = tools.map_resource_to_terriajs_type(_resource)
        # terriajs_type=data[(constants.TERRIAJS_TYPE_KEY,)]
        
    # TODO extension point (we may want to plug other schema checkers)
    if not terriajs_type:
        _stop_on_error(errors,key,'Unable to load a valid terriajs_type')

    try:

        # if not Draft4Validator.check_schema(constants.LAZY_GROUP_SCHEMA):
        #     raise Exception('schema not valid') #TODO do it once on startup (constants)
        schema = tools.resolve_schema_mapping(terriajs_type)
        #validator = Draft4Validator(constants.LAZY_GROUP_SCHEMA, resolver=resolver, format_checker=None)
        validator = Draft7Validator(schema, resolver=_SCHEMA_RESOLVER)
        # VALIDATE JSON SCHEMA
        _ret = validator.validate(config)

        # check references in case of lazy group
        _lazy_group_check_references(terriajs_type, config)

    except jsonschema.exceptions.ValidationError as e:
        #DEBUG
        #import traceback
        #traceback.print_exc()
        #TODO better message
        _stop_on_error(errors,key,'Error validating:{}'.format(str(e)))
    except Exception as e:
        #DEBUG
        #import traceback
        #traceback.print_exc()
        #TODO better message
        _stop_on_error(errors,key,'Error validating:{}'.format(str(e)))

def _lazy_group_check_references(terriajs_type, config):
    if constants.LAZY_GROUP_TYPE==terriajs_type:
            # VALIDATE REFERENCES
            items = config.get('items',None)
            for terria_view in items:
                # check if it's a lazy item
                if _get_or_bust(terria_view,'type')!=constants.LAZY_ITEM_TYPE:
                    # TODO do we need to check also remote items?
                    continue

                # if leazy item then check if target view id exists
                terria_view_id=_get_or_bust(terria_view,'id')
                view=model.ResourceView.get(terria_view_id)
                if not view:
                    # looks like it's not found, reject
                    raise Exception(_('Unable to find view with ID: {}'.format(terria_view_id)))
                elif view.view_type != constants.TYPE:
                    # should be a terriajs view actually
                    raise Exception(_('Target view with ID: {} is not of type: {}'.format(terria_view_id,constants.TYPE)))


def default_lon_e(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=180
        return
    try:
        if float(data[key])>180:
            data[key]=180
    except ValueError:
        data[key]=180

def default_lon_w(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-180
        return
    try:
        if float(data[key])<-180:
            data[key]=-180
    except ValueError:
        data[key]=-180

def default_lat_n(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=90
        return
    try:
        if float(data[key])>90:
            data[key]=90
    except ValueError:
        data[key]=90

def default_lat_s(key, data, errors, context):
    '''
    Validator providing default values 
    '''
    if not data[key]:
        data[key]=-90
        return
    try:
        if float(data[key])<-90:
            data[key]=-90
    except ValueError:
        data[key]=-90