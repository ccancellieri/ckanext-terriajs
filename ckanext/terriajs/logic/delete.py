

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


import ckanext.terriajs.logic.query as query

#TODO: listen all the possible actions which are managing:
# packages, resources, views...
@plugins.toolkit.chained_action
def resource_view_delete(next_action,context, data_dict):
    isTerriaType=data_dict.get('terriajs_type',None)
    if isTerriaType:
        # TODO checks
        # ref to query.getRelations
        #raise Exception('')
        # return query.getRelations().all()
        pass
    
    return next_action(context,data_dict)

# TODO chain this and define behaviours
def resource_view_clear(context, data_dict):
    # '''Delete all resource views, or all of a particular type.
    # :param view_types: specific types to delete (optional)
    # :type view_types: list
    # '''
    # model = context['model']

    # _check_access('resource_view_clear', context, data_dict)

    # view_types = data_dict.get('view_types')
    # model.ResourceView.delete_all(view_types)
    # model.repo.commit()
    pass

