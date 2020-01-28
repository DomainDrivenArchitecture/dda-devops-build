import os
from .credential import gopass_credential_from_env_path
from subprocess import run

STAGE = 'stage'
PROJECT_ROOT_PATH = 'project_root_path'
BUILD_COMMONS_PATH = 'build_commons_path'
MODULE = 'module'

def init_project(project, project_root_path, \
    build_commons_path, module):
    project.set_property(STAGE, os.environ.get('STAGE', 'intergation'))
    project.set_property(PROJECT_ROOT_PATH, project_root_path)
    project.set_property(BUILD_COMMONS_PATH, build_commons_path)
    project.set_property(MODULE, module)
    return project
    
def stage(project):
    return project.get_property(STAGE)

def name(project):
    return project.get_property('name')

def module(project):
    return project.get_property(MODULE)

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
