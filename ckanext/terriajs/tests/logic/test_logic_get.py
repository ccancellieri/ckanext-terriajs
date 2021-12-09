'''Tests for plugin.py.'''
import json

import ckan.plugins
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckanext.terriajs.constants as constants
import ckanext.terriajs.logic.get as getLogic
import pytest
import six
from ckan.plugins import toolkit
from ckanext.terriajs.tests.conftest import _get_terriajs_view_params

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


    @pytest.fixture(autouse=True, scope="module")
    def setup(cls):

        helpers.reset_db()

        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        if not ckan.plugins.plugin_loaded('terriajs'):
            ckan.plugins.load('terriajs')
    

    def test_we_can_enable_and_disable_an_item(self, resource):

        _resource_view_list = helpers.call_action('resource_view_list', id=resource['id'])
        
        # Check attribute not present as default
        _item = _resource_view_list[0]

        assert 'isEnabled' not in _item

        # Check enabled 
        _item_after_logic = json.loads(getLogic.item_enabled(_item['id']))
        assert 'isEnabled' in _item_after_logic
        assert _item_after_logic['isEnabled'] == True

        # Check disabled
        _item_after_logic = json.loads(getLogic.item_disabled(_item['id']))
        assert 'isEnabled' in _item_after_logic
        assert _item_after_logic['isEnabled'] == False


    def test_we_can_enable_and_disable_a_config(self, dataset):

        # Create a Resource of type constants.LAZY_GROUP_TYPE and view of type constants.TYPE
        _resource =  factories.Resource(package_id=dataset['id'], format=constants.LAZY_GROUP_TYPE)
        factories.ResourceView(**_get_terriajs_view_params(_resource, resource_type=constants.LAZY_GROUP_TYPE))
        
        # Get the view just created using the list API and filtering on type
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        _group_resource_views = [view for view in _resource_view_list if view[constants.TERRIAJS_TYPE_KEY] == constants.LAZY_GROUP_TYPE]

        # Check at least a view of type constants.LAZY_GROUP_TYPE (ideally the one we just created) exist
        assert len(_group_resource_views) > 0


        # Create another resource and two views to link in the group
        _other_resource =  factories.Resource(package_id=dataset['id'], format='csv')
        _other_views = [
            factories.ResourceView(**_get_terriajs_view_params(_other_resource)),
            factories.ResourceView(**_get_terriajs_view_params(_other_resource))
        ]

        # Get the view and set 2 items
        _group_view = _group_resource_views[0]
        _group_view[constants.TERRIAJS_CONFIG_KEY]['items'] = [
            {
                'id': _other_views[0]['id'],
                'type': constants.LAZY_ITEM_TYPE
            },
            {
                'id': _other_views[1]['id'],
                'type': constants.LAZY_ITEM_TYPE
            }
        ]

        # Update the view
        _group_view = helpers.call_action('resource_view_update', **_group_view)


        # Check if all items disabled
        config = json.loads(getLogic.config_disabled(_group_view['id']))
        items = config['catalog'][0]['items']
        assert len([item for item in items if item['isEnabled']]) == 0

        # Check if all items enabled
        config = json.loads(getLogic.config_enabled(_resource_view_list[0]['id']))
        items = config['catalog'][0]['items']
        assert len([item for item in items if not item['isEnabled']]) == 0



    def test_jinja_interpolation_works_over_mandatory_fields(self, dataset):
        """
            We test that jinja correctly interpolates data from dataset/resource into the view
            We use a simpler template than the actual one
        """

        resource = factories.Resource(package_id=dataset['id'], format='csv')
        
        view_body = _get_terriajs_view_params(resource)
        view_body[constants.TERRIAJS_CONFIG_KEY] = {
            'name': '{{dataset.title}}',
            'url': '{{resource.url}}',
            'description': '{{resource.description}}',
            'id': '{{resource.id}}',
            'type': 'csv'
        }

        _view = helpers.call_action('resource_view_create', context={}, **view_body)
        assert _view['terriajs_type'] == view_body[constants.TERRIAJS_CONFIG_KEY]['type']

        # We test actual interpolation
        # We are expecting title as interpolated value
        _item = json.loads(getLogic.item(_view['id']))

        # View title should match the metadata title
        assert _item['name'] == dataset['title']
        assert _item['url'] == resource['url']
        assert _item['id'] == resource['id']
        assert _item['description'] == resource['description']

    
    def test_that_json_strings_in_extras_are_parsed_as_json(self):

        params = {
            'extras' : [
                {
                    'key': 'json_extra',
                    'value': '{\"k1\":\"this is a json\", \"k2\": \"so it should be converted\", \"k3\":\"\\ninto a dict\"}'},
                {
                    'key': 'string_extra',
                    'value':'This is a plain string, so it should stay as it is'
                }, 
                {
                    'key':'none_extra',
                    'value': None
                }, 
                {
                    'key': 'empty_extra',
                    'value': ''
                }
            ]
        }


        dataset = factories.Dataset(**params)
        resource = factories.Resource(package_id=dataset['id'], format='csv')
        _model = getLogic._get_model(dataset_id=dataset['id'], resource_id=resource['id'])

        _extras = _model['dataset']['extras']
        
        # We expect that extra with key 'json_extra' is parsed into a json (dict)
        _json_extra = [extra for extra in _extras if extra['key'] == 'json_extra'][0]
        assert type(_json_extra['value']) is dict
        
        # We expect that extra with key 'string_extra' is parsed into a json (dict)
        _string_extra = [extra for extra in _extras if extra['key'] == 'string_extra'][0]
        if six.PY3:
            assert type(_string_extra['value']) is str
        else:
            assert type(_string_extra['value']) is unicode


        _empty_extra = [extra for extra in _extras if extra['key'] == 'empty_extra'][0]
        assert len(_empty_extra['value']) == 0


    def test_config(self, resource):
        _resource_view_list = helpers.call_action('resource_view_list', id=resource['id'])
        _config = json.loads(getLogic._config(_resource_view_list[0]['id']))
        
        assert _config
        assert resource['id'] == _config['catalog'][0]['id']


    def test_base_return_item(self, dataset):
        _params = {
            'package_id': dataset['id'],
            'url': 'http://data',
            'name': 'A nice resource',
            'format': 'csv'
        }
        _resource = helpers.call_action('resource_create', **_params)
        _resource_view_list = helpers.call_action('resource_view_list', id=_resource['id'])
        _base = getLogic._base(_resource_view_list[0]['id'])
        assert _params['url'] == _base['catalog'][0]['url']


    def test_get_model(self):

        _organization = factories.Organization()
        _dataset = factories.Dataset(owner_org=_organization['id'])
        _resource = factories.Resource(package_id=_dataset['id'], format="csv")

        _get_model = getLogic._get_model(_dataset['id'], _resource['id'])


        # When we add a resource to the dataset, the dataset parameter and _get_model['dataset'] differ for
        # resources, num_resources, metadata_modified
        # so we can't compare them altogether and we just compare the ids
        assert _dataset['id'] == _get_model['dataset']['id']

        assert _resource == _get_model['resource']
        
        assert _dataset['owner_org'] == _get_model['organization']['id']
        
        assert {'base_url': ckan.lib.helpers.url_for('/', _external=True)} == _get_model['ckan']
        assert {'base_url': constants.TERRIAJS_URL} == _get_model['terriajs']


    def test_model(self, dataset):
        _resource = factories.Resource(package_id=dataset['id'], format='csv')
        _model = getLogic._model(dataset['id'], _resource['id'])
        assert _model
