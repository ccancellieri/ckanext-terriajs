import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
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

# import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools
# import ckanext.terriajs.logic.get as get
# import ckanext.terriajs.validators as v
import logging
log = logging.getLogger(__name__)

def instance_to_dict(i):
    '''
    The Validator receive a resource instance, we need a dict...
    '''
    # TODO try using 
    # context problems
    # import ckan.lib.dictization.model_dictize as model_dictize
    # res = model_dictize.package_dictize(i, toolkit.c)
    
    resource = {'name': i.name or '',
                'url': i.url or '',
                'description': i.description or '',
                'id': i.id or '',
                'package_id': i.package_id or '',
                'format': (i.format or '').lower()
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
        resource = instance_to_dict(context['resource'])
        type = tools.get_view_type(resource)
        if not type:
            errors[key].append(_('Missing value'))
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
        resource = context['resource']
        _resource = instance_to_dict(resource)
        # _resource.update({ 'type': _get_view_type(resource)})
        
        config = tools.get_config(_resource)
        if not config:
            errors[key].append(_('Missing value'))
            raise StopOnError
        data[key] = config

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