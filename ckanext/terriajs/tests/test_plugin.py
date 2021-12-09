'''Tests for plugin.py.'''
import ckan.plugins
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckanext.terriajs.constants as constants
from ckan.plugins import toolkit
from ckanext.terriajs.tests.conftest import _get_terriajs_view_params, _get_resource_type, _get_terriajs_config

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
        

    def test_default_views_are_created_automatically(self, resource):

        _resource_view_list = helpers.call_action('resource_view_list', id=resource['id'])
        _resource_view_list_formats = [view['terriajs_type'] for view in _resource_view_list]

        # if resource format is one of the DEFAULT FORMATS
        # check if the plugin created a view for the format
        if resource['format'].lower() in constants.DEFAULT_FORMATS:
            assert resource['format'].lower() in _resource_view_list_formats

    def test_can_create_a_terriajs_view(self, resource, resource_type, terriajs_config):

        resource_type = _get_resource_type(resource)
        terriajs_config = _get_terriajs_config(resource_type)
        view_body = _get_terriajs_view_params(
            resource,
            resource_type,
            terriajs_config
        )

        terriajs_view = factories.ResourceView(**view_body)

        assert constants.TYPE == terriajs_view['view_type']


    def test_can_show_resource_view(self, terriajs_view):

        _view = helpers.call_action('resource_view_show', id=terriajs_view['id'])
        
        assert constants.TERRIAJS_CONFIG_KEY in _view
        assert constants.TERRIAJS_TYPE_KEY in _view
        assert _view['view_type'] == constants.TYPE


    def test_can_update_resource_view(self, terriajs_view):

        # We fetch the view
        _view = helpers.call_action('resource_view_show', id=terriajs_view['id'])

        params = {
            'id': _view['id'],
            'title': 'New title',
            'description': 'New description'
        }

        # We need to pass the whole view dict, not only the values that change
        _view.update(params)

        # We update the view
        _view = helpers.call_action('resource_view_update', **_view)
        
        # assert update had effect
        assert _view['title'] == params['title']
        assert _view['description'] == params['description']

