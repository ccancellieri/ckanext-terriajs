
from ckan.model import meta
from ckan.model.resource_view import ResourceView
from ckan.model.resource import Resource
from ckan.model.package import Package
from ckan.model.group import Group
from ckan.model.package_extra import PackageExtra
from ckan.model.core import State
from ckan.model import types as _types

# from sqlalchemy.dialects import postgresql

import sqlalchemy as sa

from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
_array_agg = sa.sql.functions.array_agg
_json_build_object = sa.func.json_build_object


import ckanext.terriajs.constants as constants
import logging
log = logging.getLogger(__name__)

def view_by_type():
    '''Returns the count of ResourceView not in the view types list'''

    return meta.Session.query(
                    Group.id.label('group_id'),
                    Package.id.label('package_id'),
                    Resource.id.label('resource_id'),
                    ResourceView.id,
                    Group.title.label('organization_title'),
                    Package.title.label('dataset_title'),
                    Package.notes.label('dataset_description'),
                    Resource.name.label('resource_name'),
                    Resource.description.label('resource_description'),
                    # _json_build_object(Resource.as_dict(Resource)).label('resource'),
                    # postgresql.array_agg(_json_build_object(PackageExtra.key,PackageExtra.value)).label('extras'),
                    ResourceView.config
                )\
                .select_from(Package)\
                .join(Resource, Package.id == Resource.package_id)\
                .join(ResourceView, ResourceView.resource_id == Resource.id)\
                .join(Group, Package.owner_org == Group.id)\
                .filter(ResourceView.view_type == constants.NAME)
                # .join(PackageExtra, Package.id == PackageExtra.package_id, isouter=True)\
                # .filter(PackageExtra.state == State.ACTIVE).group_by(Group.id,Package.id,Resource.id,ResourceView.id)\
                
def view_by_id(view_id):
    try:
        return view_id and view_by_type().filter(ResourceView.id==view_id).one()._asdict()
    except (NoResultFound, MultipleResultsFound) as ex:
        raise NoResultFound('Unable to find resource by view ID: '+view_id,ex)

def views_list_query(_dataset_title, _dataset_description, _resource_name):
    existing_views=view_by_type()\
        .filter(or_(_resource_name and Resource.name.like(_resource_name),
                    _dataset_title and Package.title.like(_dataset_title),
                    _dataset_description and Package.notes.like(_dataset_description)))
                # Skip DEFAULT_TYPE (full config)
                #.and_(not_(ResourceView.config.like('%\'terriajs_type\': \'{}\'%'.format(constants.DEFAULT_TYPE)))))
    return existing_views.order_by(Resource.name)

def view_details(_view_id):
    try:
        return _view_id and meta.Session.query(
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
                .filter(ResourceView.resource_id == Resource.id)\
                .one()._asdict()
                # ._asdict()
    except (NoResultFound, MultipleResultsFound) as ex:
        raise NoResultFound('Unable to find resource by view ID: '+_view_id,ex)