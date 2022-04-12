
from ckan.model import meta
from ckan.model.resource_view import ResourceView
from ckan.model.resource import Resource
from ckan.model.package import Package
from ckan.model.group import Group
from ckan.model.core import State

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
                .filter(Package.state == State.ACTIVE)\
                .filter(Resource.state == State.ACTIVE)\
                .filter(ResourceView.view_type == constants.TYPE)

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



######################################
# SELECT 
#         anon_1.package_id                        AS anon_1_package_id,
#         anon_1.resource_id                       AS anon_1_resource_id,
#         anon_1.view_id                           AS anon_1_view_id,
#         Cast(anon_2.item AS JSON) ->> (param_1)s as lazy_view_id,
#         cast(anon_2.item AS json) ->> (param_2)s AS lazy_view_type
# FROM   (
#               SELECT 
#                     package.id                                        AS package_id,
#                     resource.id                                       AS resource_id,
#                     resource_view.id                                  AS view_id,
#                     cast(resource_view.config AS json) ->> (param_3)s AS terriajs_config,
#                     resource_view.view_type                           AS view_type
#               FROM   package
#                 JOIN   resource       ON     package.id = resource.package_id
#                 JOIN   resource_view  ON     resource.id = resource_view.resource_id
#               WHERE  package.state = (state_1)s
#                 AND    resource.state = (state_2)s
#                 AND    resource_view.view_type = (view_type_1)s
#                 AND    (cast(resource_view.config AS json) ->> (param_4)s) = (param_5)s) AS anon_1,
#        (
#               SELECT anon_1.package_id AS package_id,
#                      anon_1.resource_id                                                      AS resource_id,
#                      anon_1.view_id                                                          AS view_id,
#                      json_array_elements(cast(anon_1.terriajs_config AS json) -> (param_6)s) AS item
#               FROM   (
#                     SELECT package.id                                        AS package_id,
#                             resource.id                                       AS resource_id,
#                             resource_view.id                                  AS view_id,
#                             cast(resource_view.config AS json) ->> (param_3)s AS terriajs_config,
#                             resource_view.view_type                           AS view_type
#                     FROM   package
#                     JOIN   resource
#                     ON     package.id = resource.package_id
#                     JOIN   resource_view
#                     ON     resource.id = resource_view.resource_id
#                     WHERE  package.state = (state_1)s
#                     AND    resource.state = (state_2)s
#                     AND    resource_view.view_type = (view_type_1)s
#                     AND    (cast(resource_view.config AS json) ->> (param_4)s) = (param_5)s) AS anon_1) AS anon_2
# WHERE  (cast(anon_2.item AS json) ->> (param_7)s) = (param_8)s
#         AND    anon_1.package_id = anon_2.package_id
#         AND    anon_1.resource_id = anon_2.resource_id
#         AND    anon_1.view_id = anon_2.view_id

# This is a postgresql specific implementation 
# TODO extension point to support other db types (oracle, nosql)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import func
def getRelations():
    '''
    Returns a table with LAZY loaded components
    it will resolve all the LAZY_ITEMS id
    returns a query to filter by view_id, package_id, resource_id
    '''

    session=meta.Session
    config=ResourceView.config.cast(JSON).label('config')
    # look for all the views (package and resources) having:
    # - - type as constant.NAME (terriajs)
    # - - type of the stored json constant.LAZY_GROUP_TYPE (terriajs-group)
    all_lazy_groups=session.query(
        Package.id.label('package_id'),
        Resource.id.label('resource_id'),
        ResourceView.id.label('view_id'),
        # config['items'],
        #func.lateral(func.json_array_elements(config[constants.TERRIAJS_CONFIG].cast(JSON)['items'])),
        config[constants.TERRIAJS_CONFIG_KEY].astext.label(constants.TERRIAJS_CONFIG_KEY),
        # select(func.json_array_elements(config[constants.TERRIAJS_CONFIG].cast(JSON)['items'])).column_valued('item'),
        ResourceView.view_type
    )\
    .select_from(Package)\
    .join(Resource, Package.id == Resource.package_id)\
    .join(ResourceView, Resource.id == ResourceView.resource_id)\
    .filter(Package.state == State.ACTIVE)\
    .filter(Resource.state == State.ACTIVE)\
    .filter(ResourceView.view_type == constants.TYPE)\
    .filter(config[constants.TERRIAJS_TYPE_KEY].astext == constants.LAZY_GROUP_TYPE)
    
    _sub_all_lazy_groups = all_lazy_groups.subquery()
    
    terriajs_config=_sub_all_lazy_groups.c.terriajs_config.cast(JSON).label(constants.TERRIAJS_CONFIG_KEY)
    
    # item is an array next query will explode all the items in the lazy_group
    item = func.json_array_elements(terriajs_config['items']).label('item')

    all_lazy_items=session.query(
        _sub_all_lazy_groups.c.package_id,
        _sub_all_lazy_groups.c.resource_id,
        _sub_all_lazy_groups.c.view_id,
        # terriajs_config['id'].label('lazy_group_id'), 1:1 with view_id

        # terriajs_config.label('lazy_group'),
        # func.json_to_record(terriajs_config['items']).label('item')
        item
    ).select_from(_sub_all_lazy_groups)
    # .select_from(func.json_array_elements(terriajs_config['items']))
    # .join(item)
        # .join(item) # TODO = lateral or unnest...)
    
    _sub_all_lazy_items = all_lazy_items.subquery()

    terriajs_lazy_view=_sub_all_lazy_items.c.item.cast(JSON)

    _views=session.query(
        _sub_all_lazy_groups.c.package_id,
        _sub_all_lazy_groups.c.resource_id,
        _sub_all_lazy_groups.c.view_id,
        # _sub_all_lazy_items.c.item,
        terriajs_lazy_view['id'].astext.label('lazy_view_id'),
        terriajs_lazy_view['type'].astext.label('lazy_view_type')
    ).select_from(_sub_all_lazy_items)\
    .filter(terriajs_lazy_view['type'].astext==constants.LAZY_ITEM_TYPE)\
    .filter(_sub_all_lazy_groups.c.package_id==_sub_all_lazy_items.c.package_id)\
    .filter(_sub_all_lazy_groups.c.resource_id==_sub_all_lazy_items.c.resource_id)\
    .filter(_sub_all_lazy_groups.c.view_id==_sub_all_lazy_items.c.view_id)

    _sub_views = _views.subquery()
    
    #debug
    #print(str(_views))
    #raise Exception('')
    # return _views.all()
    return _sub_views
# SELECT anon_1.package_id AS anon_1_package_id, anon_1.resource_id AS anon_1_resource_id, anon_1.view_id AS anon_1_view_id, CAST(anon_2.item AS JSON) ->> %(param_1)s AS lazy_view_id, CAST(anon_2.item AS JSON) ->> %(param_2)s AS lazy_view_type 
# FROM (SELECT package.id AS package_id, resource.id AS resource_id, resource_view.id AS view_id, CAST(resource_view.config AS JSON) ->> %(param_3)s AS terriajs_config, resource_view.view_type AS view_type 
# FROM package JOIN resource ON package.id = resource.package_id JOIN resource_view ON resource.id = resource_view.resource_id 
# WHERE package.state = %(state_1)s AND resource.state = %(state_2)s AND resource_view.view_type = %(view_type_1)s AND (CAST(resource_view.config AS JSON) ->> %(param_4)s) = %(param_5)s) AS anon_1, (SELECT anon_1.package_id AS package_id, anon_1.resource_id AS resource_id, anon_1.view_id AS view_id, json_array_elements(CAST(anon_1.terriajs_config AS JSON) -> %(param_6)s) AS item 
# FROM (SELECT package.id AS package_id, resource.id AS resource_id, resource_view.id AS view_id, CAST(resource_view.config AS JSON) ->> %(param_3)s AS terriajs_config, resource_view.view_type AS view_type 
# FROM package JOIN resource ON package.id = resource.package_id JOIN resource_view ON resource.id = resource_view.resource_id 
# WHERE package.state = %(state_1)s AND resource.state = %(state_2)s AND resource_view.view_type = %(view_type_1)s AND (CAST(resource_view.config AS JSON) ->> %(param_4)s) = %(param_5)s) AS anon_1) AS anon_2 
# WHERE (CAST(anon_2.item AS JSON) ->> %(param_7)s) = %(param_8)s AND anon_1.package_id = anon_2.package_id AND anon_1.resource_id = anon_2.resource_id AND anon_1.view_id = anon_2.view_id