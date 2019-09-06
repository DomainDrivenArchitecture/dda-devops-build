import os
from .credential import gopass_credential_from_env_path

def meissa_init_project(project):
    project.set_property('stage', os.environ.get('STAGE', 'intergation'))
    project.set_property('http_net_api_key', 
        gopass_credential_from_env_path('HTTP_NET_API_KEY_PATH'))
    project.set_property('hetzner_api_key', 
        gopass_credential_from_env_path('HETZNER_API_KEY_PATH'))
    
def hetzner_api_key(project):
   return project.get_property('hetzner_api_key')

def stage(project):
    return project.get_property('stage')

def tf_import_name(project):
    return project.get_property('tf_import_name')

def tf_import_resource(project):
    return project.get_property('tf_import_resource')
