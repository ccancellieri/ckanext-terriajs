
'''Tests for plugin.py.'''
import ckan.plugins
from ckan.plugins import toolkit
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckanext.terriajs.constants as constants
import ckanext.terriajs.tools as tools
import ckanext.terriajs.logic as getLogic
from ckan.lib.helpers import get_site_protocol_and_host
import ckanext.terriajs.logic.get as getLogic
import json
ckan_29_or_higher = toolkit.check_ckan_version(u'2.9')


class TestTerriaLogic(object):
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


    def test_item_is_disabled_return_false(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Enable groups
        isDisabled = getLogic.item_disabled(_resource_view_list[0]['id'])
        data = json.loads(isDisabled)
        assert (data['isEnabled'], False)


    def test_item_is_enabled_return_true(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Enable groups
        isEnabled = getLogic.item_enabled(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['isEnabled'], True)

    def test_is_config_disabled(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Check if disabled
        isEnabled = getLogic.config_disabled(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['catalog'][0]['isEnabled'], False)

        # Enable groups
        enabled = getLogic.item_enabled(_resource_view_list[0]['id'])

        # Check if disabled
        isDisabled = getLogic.config_disabled(_resource_view_list[0]['id'])
        data = json.loads(isDisabled)
        assert (data['catalog'][0]['isEnabled'], True)


    def test_is_config_enabled(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Check if disabled
        isEnabled = getLogic.config_enabled(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['catalog'][0]['isEnabled'], True)

        # disable groups

        disable = getLogic.item_disabled(_resource_view_list[0]['id'])

        # Check if enabled
        isEnabled = getLogic.config_enabled(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['catalog'][0]['isEnabled'], False)

    def _test_config(self):
        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Check if disabled
        isEnabled = getLogic._config(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['catalog'][0]['isEnabled'], True)

        # disable groups

        disable = getLogic.item_disabled(_resource_view_list[0]['id'])

        # Check if enabled
        isEnabled = getLogic.config_enabled(_resource_view_list[0]['id'])
        data = json.loads(isEnabled)
        assert (data['catalog'][0]['isEnabled'], False)

    def _test_url(self, app):

        _package = factories.Dataset(owner_org=self.owner_org['id'])
        _params = {
            'package_id': _package['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        # Enable groups
        # data = json.loads(isDisabled)
        # assert (data['isEnabled'], False)
        # $'''{host_url}{plugin_name}/terriajs_config/force_enabled/{resource_view_id}.json'''
        url = self.url_group_force_is_enabled.format(host = self.host_url, plugin_name = constants.TYPE, resource_view_id = _resource_view_list['id'])

        response = app.get(url)

        assert 'https://example/document.pdf' in response.body



