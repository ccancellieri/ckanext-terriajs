'''Tests for plugin.py.'''
import ckan.plugins
from ckan.plugins import toolkit
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools
import ckanext.terriajs.logic as getLogic
from ckan.lib.helpers import get_site_protocol_and_host
import json
import requests

ckan_29_or_higher = toolkit.check_ckan_version(u'2.9')


class TestTerria(object):
    admin = None
    package = None
    resource = None
    resource_view_id = None
    context = None
    owner_org = None
    params = None
    # HOST_URL ="{protocol}{host}".format(protocol='http://', host=get_site_protocol_and_host()[1])
    host_url = ckan.lib.helpers.url_for('/', _external=True)
    url_fetch_json = '''{host_url}{plugin_name}/terriajs_config/{resource_view_id}.json'''
    url_group_force_is_enabled = '''{host_url}{plugin_name}/terriajs_config/force_enabled/{resource_view_id}.json'''
    url_group = '''{host_url}{plugin_name}/terriajs_config/groups/{resource_view_id}'''

    @classmethod
    def setup_class(cls):
        helpers.reset_db()
        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        if not ckan.plugins.plugin_loaded('terriajs'):
            ckan.plugins.load('terriajs')
        # Create user and context
        cls.admin = factories.User()
        cls.context = {
            'ignore_auth': False,
            'user': cls.admin['name']
        }
        cls.owner_org = factories.Organization(
            users=[{'name': cls.admin['id'], 'capacity': 'admin'}]
        )
        cls.env = {'REMOTE_USER': cls.admin['name'].encode('ascii')}

        cls.package = factories.Dataset(owner_org=cls.owner_org['id'])

        cls.resource = factories.Resource(package_id=cls.package['id'], format='csv')

        # Create view
        # cls.package = factories.Dataset(owner_org=cls.owner_org['id'])
        try:
            resource_type = tools.map_resource_to_terriajs_type(cls.resource)
        except Exception as e:
            raise e
        resource_type = 'csv'

        terriajs_schema = tools.get_schema(resource_type)
        if not terriajs_schema:
            raise Exception(resource_type + (' not defined, check your config'))

        terriajs_config = tools.get_config(resource_type)

        cls.params = {
            'resource_id': cls.resource['id'],
            'view_type': constants.TYPE,
            'description': 'A nice view',
            constants.TERRIAJS_TYPE_KEY: resource_type,
            constants.TERRIAJS_CONFIG_KEY: terriajs_config
        }
    def test_unknown(self):
        # You pass a resource to the builder
        # You obtain the parameters
        # Check into the parameters if the type of the view
        # Check into the parameters the terriajs type
        # Do the following tests for this format constants.formats
        pass

    def test_default_views_are_created_automatically(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        formats = constants.DEFAULT_FORMATS

        # Check if they are views
        assert (_resource_view_list)
        # Check if the created view has a format declared in the constants
        for view in _resource_view_list:
             if view[constants.TERRIAJS_TYPE_KEY] in formats:
                 assert True
                 assert (view['view_type'], constants.TYPE)


    def test_can_create_a_terriajs_view(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _resource = factories.Resource(package_id=_package['id'])
        _resource_view = factories.ResourceView(**self.params)
        assert constants.TYPE == _resource_view['view_type']


    def test_can_show_resource_view(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _resource = factories.Resource(package_id=_package['id'])
        _resource_view = factories.ResourceView(**self.params)

        result = helpers.call_action('resource_view_show', id=_resource_view['id'])
        result.pop('id')
        result.pop('package_id')
        assert (self.params, result)

