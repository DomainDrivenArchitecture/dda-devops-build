import os
from .credential import gopass_credential_from_env_path
from subprocess import run

STAGE = 'stage'
HTTP_NET_API_KEY = 'http_net_api_key'
HETZNER_API_KEY = 'hetzner_api_key'
PROJECT_ROOT_PATH = 'project_root_path'
BUILD_COMMONS_PATH = 'build_commons_path'

def meissa_init_project(project, project_root_path, build_commons_path):
    project.set_property(STAGE, os.environ.get('STAGE', 'intergation'))
    project.set_property(PROJECT_ROOT_PATH, project_root_path)
    project.set_property(BUILD_COMMONS_PATH, build_commons_path)
    project.set_property(HTTP_NET_API_KEY, \
        gopass_credential_from_env_path('HTTP_NET_API_KEY_PATH'))
    project.set_property(HETZNER_API_KEY, \
        gopass_credential_from_env_path('HETZNER_API_KEY_PATH'))
    return project
    
def hetzner_api_key(project):
   return project.get_property(HETZNER_API_KEY)

def stage(project):
    return project.get_property(STAGE)

def module(project):
    return project.get_property('name')

def project_root_path(project):
    return project.get_property(PROJECT_ROOT_PATH)

def build_commons_path(project):
    return project.get_property(BUILD_COMMONS_PATH)

def build_target_path(project):
    return project_root_path(project) + 'target/' + project.name + '/'

def tf_import_name(project):
    return project.get_property('tf_import_name')

def tf_import_resource(project):
    return project.get_property('tf_import_resource')

def initialize_target(project):
    run('rm -rf ' + build_target_path(project), shell=True)
    run('mkdir -p ' + build_target_path(project), shell=True)
    run('cp *.tf ' + build_target_path(project), shell=True)
    run('cp *.tfars ' + build_target_path(project), shell=True)
    run('cp *.edn ' + build_target_path(project), shell=True)
