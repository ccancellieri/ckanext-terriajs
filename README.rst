.. contents:: Table of Contents
   :depth: 2


|


Description
===========

.. _plugin

The TerriaJS view plugin provide an extensible and highly configurable set of views ready for TerriaJS.

It leverages over JSON schema to facilitate and speedup the configurations editing for each configured type (csv, wms, wmts, etc).

The plugin also presents an embedded overview of the result showing the layer into an Iframe.


**Image below**: **ckanext-terriajs** loaded iframe on CKAN.

|

.. image:: docs/img/terriajs_load.png
   :class: with-shadow
   :width: 600 px
   :alt: Loaded view

|


The terriajs view plugin can link existing views and group them into virtual (lazy loaded) groups of configurations.

It also allows you to use jinja2 template to fill in informations into terriajs views cherry picking the title, description and more directly from the dataset or the target resource.

The dynamic approach (lazy-load + jinja2) allows you to create views which are always in synch with the changes made over the metadata and the resource to show.

The plugin is also able to automatically create a configurable sets ove views (you define what you want to have automatically and how).

Out of the box it is already capable to automatically create views over wms, mvt, csv formats. 

|


Validation
==========

.. _validation

The plugin is heavily based on a JSON + JSON-SCHEMA approach.

It ships also an ui form generator which is able to drive the user into the creation or modification of a new (or existing) view.

The **frontend** js library used is `json-editor <https://github.com/json-editor/json-editor>`__ but there's also an `ACE editor <https://ace.c9.io/>`__ and `AJV validation <https://ajv.js.org/>`__ to simplify quick editing from experienced editors.

Both UI js libraries are configured to provide UI validation based on JSON schema.

|

.. image:: docs/img/terriajs_group_frontend_validation.png
   :width: 800 px
   :alt: frontend validation

|

At the **backend** side the plugin leverages over `jsonschema <https://python-jsonschema.readthedocs.io/en/stable/>`__.
This is the sole python dependency **required to install**.
Thanks to this additional validation the rest API is covered with validation.

|

All the json-schema (draft4) supported by terriajs v7 are provided into a folder in the source tree (tbt).

|



Dynamic models (lazy-loaded)
============================

.. _lazy_models

The terriajs view plugin defines a small set of __special__ types which are used to resolve at request time existing views, so you can easily keep connected them into dynamic groups by view id.

The special resource type 'terriajs-group' infact defined by a schema which allows you to search (using ui) and connect existing terriajs views (csv, mvt, etc).

The item pointing to an existing terriajs view is called terriajs-view (ref. image below), but an editor might not be informed about these internal details unless he wants to use the free form json editor.

With this approach an administrator/editor is able to create dynamic collections which will be __resolved__ at each request, giving you a fresh copy shipping all the changes performed by editors to each connected view (the views can also be dynamically resolved thanks to jinja2 templating approach)


|

.. image:: docs/img/terriajs_terriajs_group.png
   :width: 800 px
   :scale: 50 %
   :alt: terriajs-group

|

Note:
-----

This functionnality stress a lot the database and can be cpu intensive, so try to limit the amount of nodes resolved at runtime or cache them.

|

Terriajs item creation and the jinja2 interpolation
---------------------------------------------------

During the creation of a resource the Terriajs plugin view can provide on the fly configurations to provide a default view based on the _format_ of the resource (linked or uploaded).

Thanks to the json-schema mapping (provided by the configuration) and to the PATH_SCHEMA and PATH_TEMPLATE folders ckan can undestand which json schema file should be used with that specific type.

In addition to that to create on the fly also the view that type needs an initializer to specify all the item fields.

f.e.: an CSV item has:

  {
    "id":...
    "name":...
    "description":..
    "url":...
    "type":"csv"
    [optionals]
  }

Most parts of the snippet above are provided by a predefined _template_ which must be present into the _template_ folder (PATH_TEMPLATE).

There are some special templates like _Catalog_ which are used to provide cofigurations wrapped by the Catalog (ref to the template for details) or directly the item (in that case the Catalog template wont be used).

Once the terriajs view or the view editor page is filled in with the _template_ the user can start customizing it.

But what if we want to name the item in the same way of the resource, or the dataset or apply some logic to it?

Well all the above mechanism is also usable with jinja2.

In the image below you may see a resolver which will gather information from the schema mapping, the templates (but only during the first time creation/edit) and a data model.

So for each view, the _template_ or the configuration itself can leverage over a template and the full model of the package + resource + organization to provide good and standardized descriptions, names, etc.

The _resolver_ will take care of interpolate each first level value of each terriajs view requested.

If some fields like _featureInfoTemplate_ contains special charachters incompatible with jinja2 (like Mustache syntax) you have to configure the FIELDS_TO_SKIP parameter.

|

.. image:: docs/img/terriajs_resolve_items.png
   :width: 800 px
   :scale: 50 %
   :alt: terriajs-resolve-items

|

Note:
-----

All of the above is also applicable to the terriajs-groups mechanism which will resolve the target view, iterpolate with jinja2+model and then return it.



Reference Integrity
===================

.. _reference integrity

Having a lazy load root node 'terriajs-group' adds the challenge to keep reference integrity (1-to-many) from the terriajs-group to the target childrens (existing views).

The terriajs view plugin forbids the deletion of existing referenced views so a terriajs-group will always be consistent.

|

Note
----

This plugin leverages over postgres + json approach **NOT STORING OR CREATING ANY ADDITIONAL TABLE**, I consider this a plus for any migration (at the cost of a bit of complexity in terms of query and reference integrity).

Reference integrity will check (on the backend) if the id of the target view (resolved dynamically) is not existent 

|

Trying to send a not valid id
-----------------------------

|

.. image:: docs/img/terriajs_group_reference_integrity_check_1.png
   :width: 800 px
   :scale: 50 %
   :alt: ref integrity step 1

|

Reporting the error to the editor
---------------------------------

|

.. image:: docs/img/terriajs_group_reference_integrity_check_2.png
   :width: 800 px
   :scale: 50 %
   :alt: ref integrity step 2

|


Referenced View deletion
------------------------


The plugin warns the owner of the view providing the list (hrefs) of existing 'terriajs-group' pointing to his view.

|

.. image:: docs/img/terriajs_item_reference_integrity_check_on_children_deletion.png
   :width: 800 px
   :scale: 50 %
   :alt: Unable to delete a children

|


Tools
=====

.. _tools

The UI is also providing a quite extensive set of buttons (copy to clipboard) to easily customize (in case of need) the view with static details.

It also provides a set of buttons to test the resulting API endpoints (which will be used to connect an existing terriajs installation)

|

.. image:: docs/img/terriajs_frontend_tools.png
   :width: 800 px
   :alt: Frontend tools


|

API
===

.. _api

CKAN standard action
--------------------

This is an example on how to create a terriajs view via API with python



    import requests
    
    def create_resource_view(payload, endpoint, headers):
        req_v = requests.post(endpoint, json=payload, headers=headers)
        if req_v.status_code != 200:
            print('Error while creating the view : {0}'.format(req_v.content))
        else:
            print("Resource View has been created")
            
    payload = {
        "resource_id": '{THE RESOURCE ID}',
        "title": 'Map',
        "description": 'description',
        "view_type": 'terriajs',
        'terriajs_type': 'csv',
        'terriajs_config': '{"type":"csv", "id":"test", "name":"csv_name.csv", "url":"http://link_to_resource" }'
    }

    # Site url
    endpoint = '{CKAN_URL}/api/3/action/resource_view_create'

    headers = {'Authorization': {API_TOKEN}, 'Content-type': 'application/json'}

    create_resource_view(payload, endpoint, headers=headers)

|    


Terriajs additional endpoints
-----------------------------

In addition to the ckan standard action (create_view, etc) the plugin is also providing a new set of blueprint endpoints (read only):

|

    /terriajs/describe

describe an existing view by id, used by terriajs-group

|

    /terriajs/search

search an existing view by resource or dataset title/description, used by terriajs-group)

|

    /terriajs/schema/<filename>

 a proxy to resolve relative schema references (ckan can work also as source of schemas in case you don't have a static repository)

|

    /terriajs/config/[<enabled|disabled>/]<uuid>.json

an endpoint to return a valid and dinamically resolved and interpolated full terriajs configuration (used by the **preview**).

You can set **enabled** to have all the items (recursively) enabled and displayed over the map or **disabled** to force disabling.

|

    /terriajs/item/[<enabled|disabled>/]<uuid>.json


While */config/* returns a fully functional configuration catalog, this endpoint to return the configured (unwrapped) **item** (dinamically resolved and interpolated)

You can set **enabled** to have all the items (recursively) enabled and displayed over the map or **disabled** to force disabling.

|

Extensions
==========

The full lost of terriajs plugin configuation parameters are documented under `constants.py <https://bitbucket.org/cioapps/ckanext-terriajs/src/master/ckanext/terriajs/constants.py>`__

The terriajs configuration item type is defined into the configuration with a target json-schema.

The configuration is shippend in a file called `type-mapping.json <https://bitbucket.org/cioapps/ckanext-terriajs/src/master/type-mapping.json>`__ which is a serialized dict (a map):


    {
        'terria-js-type': 'URI'
    }



**terria-js-type** is the terriajs item type ref `here <https://docs.terria.io/guide/connecting-to-data/catalog-items/>`__ for a complete list.

**URI** can be:
  
  - relative to the PATH_SCHEMA folder (see constants.py)

  - http link to a target json schema


On startup the plugin check the list to understand which item is supported and add that format to the list.

When you add a resource to a dataset the **type** is mapped over type-mapping configuration and the matching json-schema is loaded to provide validation (frontend and backend side)

Based on the selected schema a different UI will be automatically provided and validated thanks to json-editor.

The json-schma will define all the required fields and the minimum requirements to have a good and valid json (frontend interactive validation/creation).



|

Requirements
============

Before installing ckanext-terriajs, make sure that you have installed the following:

* CKAN 2.8 and above
* terriajs 7
* Postgresql > 9.4

|

Installation
============

We are not providing pip package to install please use:

    git clone https://bitbucket.org/cioapps/ckanext-terriajs.git
    cd ckanext-terriajs
    pip install -r requirements.txt
    python setup.py install

Be sure to configure at least the mandatory settings into your production.ini file

|


Configuration
=============

Copy and edit the type-mapping.json to the config folder:

    cp ./type-mapping.json /etc/ckan/default/terriajs-type-mapping.json

Enable the plugin into production.ini

If you desire to make it enabled by default (recommended):

    my_default_view = ...  terriajs

    # Define which views should be created by default
    # (plugins must be loaded in ckan.plugins)

    ckan.views.default_views =  %(my_default_view)s

    ckan.plugins = %(my_default_view)s ...

If you just want to have the plug loaded:


    ckan.plugins = terriajs ...


Please ref to constants.py for an updated list of available parameters:

    ckanext.terriajs.url = http://localhost:8080
    ckanext.terriajs.schema.type_mapping = /etc/ckan/default/terriajs-type-mapping.json

|

Development
===========

To install ckanext-terriajs for development, activate your CKAN virtualenv and do::

    git clone https://bitbucket.org/cioapps/ckanext-terriajs.git
    cd ckanext-terriajs
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    python setup.py develop
    
|


Tests
=====


To run the tests:


1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate


2. From the CKAN root directory (not the extension root) do::


    pytest --ckan-ini=test.ini ckanext/terriajs/tests

