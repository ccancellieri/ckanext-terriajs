

from sqlalchemy.sql.operators import as_
from sqlalchemy.sql.sqltypes import ARRAY, TEXT
import ckan.plugins as plugins
import ckanext.terriajs.constants as constants

from ckan.model.resource_view import ResourceView
from ckan.model.resource import Resource
from ckan.model.package import Package
from ckan.model.core import State

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import cast
from sqlalchemy import func, Integer
from sqlalchemy.sql import select


import ckan.plugins.toolkit as toolkit
_ = toolkit._
h = toolkit.h

import ckan.logic as logic
_check_access = logic.check_access


import ckanext.terriajs.logic.query as query

#TODO: listen all the possible actions which are managing:
# packages, resources, views...
# resource_view_update')(context, data)
# data = get_action('resource_view_create

def _isOfTerriaType(data_dict):
    return data_dict.get(constants.TERRIAJS_TYPE_KEY,None)
    

@plugins.toolkit.chained_action
def resource_view_update(next_action,context, data_dict):
    #TODO:
    # 1. move to logic.update.py
    # 2. check the changes from what's over the db (with _get_view)

    # if _isOfTerriaType(data_dict):
    #     _check_access('resource_view_update', context, data_dict)
    #     # TODO policy... do we need to freeze changes untill it's 'connected'?
    #     # at the moment we just pass
    #     pass

    return next_action(context,data_dict)


@plugins.toolkit.chained_action
def resource_view_delete(next_action,context, data_dict):
    
    if _isOfTerriaType(data_dict):
        _check_access('resource_view_delete', context, data_dict)
        # TODO checks
        # ref to query.getRelations (but we are checking input via schema validation)
        #raise Exception('')
        view_id = data_dict.get('id', None)
        sub_q = query.getRelations()
        views = context['session'].query(
                sub_q.c.package_id,
                sub_q.c.resource_id,
                sub_q.c.view_id,
                sub_q.c.lazy_view_id
            ).select_from(sub_q)\
            .filter(sub_q.c.lazy_view_id==view_id).all()
            # .filter((sub_q.c.lazy_view_id==view_id) | (sub_q.c.view_id==view_id)).all()
        if views:
            # header=None
            # for c in sub_q.columns:
            #     if header:
            #         header='{},{}'.format(header,c.name)
            #     else:
            #         header='{}'.format(c.name)
            # h.flash_error(header)
            error_msg='<h2>Can\'t delete this view, it is referenced by:</h2><p><ol>'
            for v in views:
                # h.flash_error(str(v))
                package_id=v[0]
                resource_id=v[1]
                view_id=v[2]
                url=h.url_for('resource_view', id=package_id, resource_id=resource_id, view_id=view_id, qualified=True)
                error_msg+='<li><a class="btn btn-info" data-toggle="tooltip" data-placement="top"\
                            title="Click to open the view referencing preventing deletion"\
                            href=\"{}\" target="_blank">Resource id: {}</a></li>'.format(url,resource_id)   
            error_msg+='</ol></p>'
            h.flash_error(error_msg,allow_html=True)
                # h.flash_error(h.url_for('resource_view', id=package_id, resource_id=resource_id, view_id=view_id, qualified=True))
            # forbid deletion
            return

    # raise Exception('')
    return next_action(context,data_dict)

# TODO chain this and define behaviours
def resource_view_clear(context, data_dict):
    # '''
    # Delete all resource views, or all of a particular type.
    # :param view_types: specific types to delete (optional)
    # :type view_types: list
    # '''
    if constants.PREVENT_CLEAR_ALL:
        h.flash_error('Prevent resource_view_clear is enabled',allow_html=True)
        return

    # _check_access('resource_view_clear', context, data_dict)

    # view_types = data_dict.get('view_types')
    # model.ResourceView.delete_all(view_types)
    # model.repo.commit()
    pass

