# https://docs.pytest.org/en/6.2.x/fixture.html#requesting-fixtures
# Fixtures in this file are automatically discovered by Pytest
#
# If there exist a fixture called user, e.g:
#
# @pytest.fixture()
# def user():
#   return factories.User()
#
# Any method can declare a parameter user, and Pytest will call the fixture and provide the result

import pytest
import ckan.tests.factories as factories
import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools

@pytest.fixture()
def user():
    return factories.User()


@pytest.fixture()
def organization():
    return factories.Organization()


@pytest.fixture
def dataset(organization):
    return factories.Dataset(owner_org=organization['id'])


@pytest.fixture
def resource(dataset):
    return factories.Resource(package_id=dataset['id'], format='csv')


@pytest.fixture
def terriajs_view(resource, resource_type, terriajs_config):
    
    params = _get_terriajs_view_params(
        resource,
        resource_type,
        terriajs_config
    )

    return factories.ResourceView(**params)



@pytest.fixture
def resource_type(resource):    
    return _get_resource_type(resource)


# We define this method aside from the fixture so we can call this directly
def _get_resource_type(resource):
    try:
        _resource_type = tools.map_resource_to_terriajs_type(resource)
    except Exception as e:
        raise e

    return _resource_type


@pytest.fixture
def terriajs_config(resource_type):
    return _get_terriajs_config(resource_type)


# We define this method aside from the fixture so we can call this directly
def _get_terriajs_config(resource_type):
    return tools.get_config(resource_type)


# We define this method aside from the fixture so we can call this directly
def _get_terriajs_view_params(
    resource = None,
    resource_type = None,
    terriajs_config = None
    ):

    if resource is None:
        resource = factories.Resource()

    resource_id = resource['id']
    view_type = constants.TYPE
    description = 'A nice view'
    title = 'View Title'


    if resource_type is None:
        resource_type = _get_resource_type(resource)

    if terriajs_config is None:
        terriajs_config = _get_terriajs_config(resource_type)

    return {
        'resource_id': resource_id,
        'view_type': view_type,
        'description': description,
        'title': title,
        constants.TERRIAJS_TYPE_KEY: resource_type,
        constants.TERRIAJS_CONFIG_KEY: terriajs_config
     }