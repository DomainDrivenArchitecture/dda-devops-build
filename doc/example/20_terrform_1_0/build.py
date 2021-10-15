from os import environ
from pybuilder.core import task, init
from ddadevops import *

name = 'my-project'
MODULE = 'my-module'
PROJECT_ROOT_PATH = '../../..'

class MyBuild(AwsBackendPropertiesMixin, DevopsTerraformBuild):
    pass


@init
def initialize(project):
    project.build_depends_on('ddadevops>=0.13.2')
    stage = environ['STAGE']
    print('Doing stage: ', stage)
    config = create_devops_terraform_build_config(stage,
                                                  PROJECT_ROOT_PATH,
                                                  MODULE,
                                                  {},
                                                  use_workspace=False,
                                                  terraform_version=1.0)
    config = add_aws_backend_properties_mixin_config(config, 'prod')
    build = MyBuild(project, config)        
    build.initialize_build_dir()


@task
def plan(project):
    build = get_devops_build(project)
    build.plan()


@task
def tf_apply(project):
    build = get_devops_build(project)
    build.apply(True)


@task
def apply(project):
    build = get_devops_build(project)
    build.apply(True)


@task
def destroy(project):
    build = get_devops_build(project)
    build.destroy(True)

@task
def tf_import(project):
    build = get_devops_build(project)
    build.tf_import('aws_route53_record.v4', 'my-resource-id')