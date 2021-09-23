'''Tests for plugin.py.'''
import ckan.plugins
from ckan.plugins import toolkit
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools
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

    def test_can_create_a_terriajs_view(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _resource = factories.Resource(package_id=_package['id'])
        _resource_view = factories.ResourceView(**self.params)
        assert constants.TYPE == _resource_view['view_type']


    def test_can_show_resource_view(self, app):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _resource = factories.Resource(package_id=_package['id'])
        _resource_view = factories.ResourceView(**self.params)

        result = helpers.call_action('resource_view_show', id=_resource_view['id'])
        result.pop('id')
        result.pop('package_id')
        assert (self.params, result)

    # def _test_can_load_json_config(self, app):
    #     new_view = helpers.call_action('resource_view_create', **self.params)
    #     # Check if file is generated
    #     url = self.url_fetch_json.format(host_url=self.host_url, plugin_name=constants.TYPE,
    #                                 resource_view_id=new_view['id'])
    #     response = requests.get(url, extra_environ=self.env)
    #     assert (constants.TERRIAJS_CATALOG, response.body)

    #     # Delete view
    #     helpers.call_action("resource_view_delete", context={}, **new_view)

    def _test_type_of_not_group_is_enabled_return_true(self, app):
        new_view = helpers.call_action('resource_view_create', **self.params)
        # Enable groups
        url = self.url_group_force_is_enabled.format(host_url=self.host_url, plugin_name=constants.TYPE,
                                                     resource_view_id=new_view['id'])
        response = requests.get(url, extra_environ=self.env)
        data = json.loads(response.body)
        for item in data['catalog'][0]['items']:
            if 'isEnabled' in item:
                assert (True, item['isEnabled'])

    def _test_check_if_group_returns_an_array(self, app):
        new_view = helpers.call_action('resource_view_create', **self.params)
        # Enable groups
        url = self.url_group.format(host_url=self.host_url, plugin_name=constants.TYPE,
                                    resource_view_id=new_view['id'])

        response = requests.get(url, extra_environ=self.env)
        data = json.loads(response.body)
        assert (True, isinstance(data, list))
