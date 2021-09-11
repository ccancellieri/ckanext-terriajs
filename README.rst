ckanext-terriajs
=====================================

|

This plugin provide an extensible and highly configurable view for TerriaJS.

It leverages over JSON schema to facilitate and speedup the configurations editing for each configured type (csv, wms, wmts, etc).

The plugin also presents an embedded overview of the result showing the layer into an Iframe and a set of API to fetch the created configuration and more.

The dynamic approach to the configurations (jinja2 template) allows you to create views which are always in synch with the changes made over the metadata and the resource to show.

The terriajs view plugin infact allows you to dinamically link existing images and group them into virtual (lazy loaded) groups of configurations.

It also allows you to use jinja2 template to fill in informations into the views cherry picking the title, description and more directly from the dataset or the target resource.

The plugin is also able to automatically create a configurable sets ove views (you define what you want to have automatically and how).

Without any configuration it is shipping wms, mvt, csv automatic view creation out of the box. 

Validation
==========

The plugin is heavily based on a JSON + JSON-SCHEMA approach.

It ships also an ui form generator which is able to drive the user into the creation or modification of a new (or existing) view.

The **frontend** js library used is **json-editor** (https://github.com/json-editor/json-editor) but there's also an **ACE** editor (https://ace.c9.io/) and **AJV** validation (https://ajv.js.org/) to simplify quick editing from experienced editors.

Both UI js libraries are configured to provide UI validation based on JSON schema.


.. image:: docs/img/terriajs_group_frontend_validation.png
    :alt: frontend validation

At the **backend** the plugin leverages over **jsonschema** (https://python-jsonschema.readthedocs.io/en/stable/ is the unique python dependency required to install) so also the rest API is covered with a validation providing to the user messages in case of error (json not compliant with the json-schema). 

Lazy models
===========

The terriajs view plugin defines a _special_ type which is resolved at request time so you can easily keep connected existing views into dynamic groups by view id.

The special resource type 'terriajs-group' infact is binded (configurable) to a schema which allows you to search (using ui) and connect existing terriajs views (csv, mvt, etc)

With this approach an administrator is able to create dynamic collections which will be _resolved_ at each request, giving you a fresh copy shipping all the changes perfomed by editors to each connected view (the views can also be dynamically resolved thanks to jinja2 templating approach)


Reference Integrity
===================

Having a lazy load root node 'terriajs-group' adds the challenge to keep reference integrity (1-to-many) from the terriajs-group to the target childrens (existing views).

The terriajs view plugin forbids the deletion of existing referenced views so a terriajs-group will always be consistent.

**Note** that this plugin leverages over postgres + json approach **NOT STORING OR CREATING ANY ADDITIONAL TABLE**, I consider this a plus for any migration (at the cost of a bit of complexity in terms of query and reference integrity).

Reference integrity will check (on the backend) if the id of the target view (resolved dynamically) is not existent 

.. image:: docs/img/terriajs_group_reference_integrity_check_1.png
    :alt: ref integrity step 1

Reporting the error to the editor

.. image:: docs/img/terriajs_group_reference_integrity_check_2.png
    :alt: ref integrity step 2


Referenced View deletion children side
======================================
The plugin warns the owner of the view providing the list (hrefs) of existing 'terriajs-group' pointing to his view.

.. image:: docs/img/terriajs_item_reference_integrity_check_on_children_deletion.png
    :alt: Unable to delete a children

Tools
=====

The UI is also providing a quite extensive set of buttons (copy to clipboard) to easily customize (in case of need) the view with static details.

It also provides a set of buttons to test the resulting API endpoints (which will be used to connect an existing terriajs installation)

.. image:: docs/img/terriajs_frontend_tools.png
    :alt: Frontend tools

API
===

In addition to the cksn standard action (create_view, etc)

On the backend the plugin adds a set of blueprint endpoints to:

/terriajs/describe

describe an existing view by id, used by terriajs-group

/terriajs/search

search an existing view by resource or dataset title/description, used by terriajs-group)

/terriajs/schema/<filename>

 a proxy to resolve relative schema references (ckan can work also as source of schemas in case you don't have a static repository)

/terriajs/config/[<enabled|disabled>/]<uuid>.json

 an endpoint to return a valid and dinamically resolved and interpolated full terriajs configuration (used by the **preview**).

You can set **enabled** to have all the items (recursively) enabled and displayed over the map or **disabled** to force disabling.

/terriajs/item/[<enabled|disabled>/]<uuid>.json

While */config/* returns a fully functional configuration catalog, this endpoint to return the configured (unwrapped) **item** (dinamically resolved and interpolated)

You can set **enabled** to have all the items (recursively) enabled and displayed over the map or **disabled** to force disabling.


Extensibility
=============

You can define

.. image:: docs/img/terriajs_load.png
    :alt: Loaded view


|

**ckanext-terriajs** Adds a view to the resource and that will enable the creation of **ckanext-terriajs** views on the resource.

**Image below**: Creating a **ckanext-terriajs** view.

|

.. image:: docs/img/creating_terriajs_view.png
    :alt: Creating a ckanext-terriajs view

|

**Image below**: You can set the **name**, **description** and the **terriajs JSON configuration**.
**ckanext-terriajs**

|

.. image:: docs/img/config.jpg
    :alt: terriajs config

|

**Image below**: **ckanext-terriajs** loaded iframe on CKAN.
|

.. image:: docs/img/terriajs_load.png
    :alt: Loaded view

|
|

Requirements
------------

Before installing ckanext-terriajs, make sure that you have installed the following:

* CKAN 2.8 and above

|
|

Installation
------------

We are not providing pip package to install please use:

    git clone https://bitbucket.org/cioapps/ckanext-terriajs.git
    cd ckanext-terriajs
    python setup.py install

|
|

Configuration
-------------

You must make sure that the following is set in your CKAN config::

    ckanext.terriajs.default.name=TerriaJS
    ckanext.terriajs.always_available=True
    ckanext.terriajs.default.title=TerriaJS view
    ckanext.terriajs.icon=globe
    ckanext.terriajs.url=http://localhost:8080
    ckanext.terriajs.default.formats=['csv']
  

|
|

Development
-----------
To install ckanext-terriajs for development, activate your CKAN virtualenv and do::

    git clone https://bitbucket.org/cioapps/ckanext-terriajs.git
    cd ckanext-terriajs
    python setup.py develop
    
|
|

Tests
-----
To run the tests:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate


2. From the CKAN root directory (not the extension root) do::

    pytest --ckan-ini=test.ini ckanext/terriajs/tests

