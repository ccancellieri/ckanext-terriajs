
import os
import json

import constants

def read_template(name):
    '''
    provides a reader for local template definitions
    '''
    # TODO increase security should be/ensure to be under schema_path folder
    return _json_load(constants.PATH_TEMPLATE, name)

def read_schema(name):
    '''
    provides a reader for local schema definitions
    '''
    # TODO increase security should be/ensure to be under schema_path folder
    return _json_load(constants.PATH_SCHEMA, name)

def _json_load(folder, name):
    '''
    Maight be used with caution, the 'folder' param is considered trusted (may never be exposed as parameter)
    '''
    try:
        file=os.path.realpath(os.path.join(folder,name))
        # ensure it's a file and is readable
        isfile=os.path.isfile(file)
        # ensure it's a subfolder of the project
        issafe = os.path.commonprefix([file, folder]) == folder
        if isfile and issafe:
            with open(file) as s:
                return json.load(s)
        else:
            return None
    except Exception as ex:
        raise Exception(_("Schema named: {} not found, please check your schema path folder: {}".format(name,str(ex))))