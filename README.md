# dda-devops-build

[![Slack](https://img.shields.io/badge/chat-clojurians-green.svg?style=flat)](https://clojurians.slack.com/messages/#dda-pallet/) | [<img src="https://meissa-gmbh.de/img/community/Mastodon_Logotype.svg" width=20 alt="team@social.meissa-gmbh.de"> team@social.meissa-gmbh.de](https://social.meissa-gmbh.de/@team) | [Website & Blog](https://domaindrivenarchitecture.org)

dda-devops-build provide a envioronment to tie several DevOps tools together for easy interoperation. Supported tools are:
* aws with
  * simple api-key auth
  * mfa & assume-role auth
* hetzner with simple api-key auth
* terraform v0.11, v0.12 supporting
  * local file backends
  * s3 backends
* docker / dockerhub
* user / team credentials managed by gopass
* dda-pallet

# Setup

```
sudo apt install python3-pip
sudo pip3 install pip3 --upgrade --user
pip3 install pybuilder ddadevops deprecation --user
export PATH=$PATH:~/.local/bin

# in case of using terraform
pip3 install python-terraform --user

# in case of using AwsMixin
pip3 install boto3 --user

# in case of using AwsMfaMixin
pip3 install boto3 mfa --user
```

# Example Build

lets assume the following poject structure

```
my-project
   | -> my-module
   |       | -> build.py
   |       | -> some-terraform.tf
   | -> an-other-module
   | -> target  (here will the build happen)
   |       | -> ...
```

```
from pybuilder.core import task, init
from ddadevops import *

name = 'my-project'
MODULE = 'my-module'
PROJECT_ROOT_PATH = '..'

class MyBuild(DevopsTerraformBuild):
    pass


@init
def initialize(project):
    project.build_depends_on('ddadevops>=0.5.0')
    account_name = 'my-aws-account-name'
    account_id = 'my-aws-account-id'
    stage = 'my stage i.e. dev|test|prod'
    additional_vars = {'var_to_use_insied_terraform': '...'}
    additional_var_files = ['variable-' + account_name + '-' + stage + '.tfvars']
    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,
                                                  MODULE, additional_vars,
                                                  additional_tfvar_files=additional_var_files)
    build = MyBuild(project, config)
    build.initialize_build_dir()


@task
def plan(project):
    build = get_devops_build(project)
    build.plan()


@task
def apply(project):
    build = get_devops_build(project)
    build.apply()

@task
def destroy(project):
    build = get_devops_build(project)
    build.destroy()

@task
def tf_import(project):
    build = get_devops_build(project)
    build.tf_import('aws_resource.choosen_name', 'the_aws_id')
```

## Feature aws-backend

Will use a file `backend.dev.live.properties` where dev is the [account-name], live is the  [stage].

the backend.dev.live.properties file content:
```
key = ".."
region = "the aws region"
profile = "the profile used for aws"
bucket = "the s3 bucket name"
kms_key_id = "the aws key id"
```

the build.py file content:
```
class MyBuild(AwsBackendPropertiesMixin, DevopsTerraformBuild):
    pass


@init
def initialize(project):
    project.build_depends_on('ddadevops>=0.5.0')
    account_name = 'my-aws-account-name'
    account_id = 'my-aws-account-id'
    stage = 'my stage i.e. dev|test|prod'
    additional_vars = {}
    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,
                                                  MODULE, additional_vars)
    config = add_aws_backend_properties_mixin_config(config, account_name)
    build = MyBuild(project, config)
    build.initialize_build_dir()
```

## Feature aws-mfa-assume-role

In order to use aws assume role in combination with the mfa-tool (`pip install mfa`):

the build.py file content:
```
class MyBuild(class MyBuild(AwsMfaMixin, DevopsTerraformBuild):
    pass


@init
def initialize(project):
    project.build_depends_on('ddadevops>=0.5.0')
    account_name = 'my-aws-account-name'
    account_id = 'my-aws-account-id'
    stage = 'my stage i.e. dev|test|prod'
    additional_vars = {}
    config = create_devops_terraform_build_config(stage, PROJECT_ROOT_PATH,
                                                  MODULE, additional_vars)
    config = add_aws_backend_properties_mixin_config(config, account_name)
    config = add_aws_mfa_mixin_config(config, account_id, 'eu-central-1',
                                      mfa_role='my_developer_role',
                                      mfa_account_prefix='company-',
                                      mfa_login_account_suffix='users_are_defined_here')
    build = MyBuild(project, config)
    build.initialize_build_dir()

@task
def access(project):
    build = get_devops_build(project)
    build.get_mfa_session()
```

## Feature DdaDockerBuild

The docker build supports image building, tagging, testing and login to dockerhost.
For bash based builds we support often used script-parts as predefined functions [see install_functions.sh](src/main/resources/docker/image/resources/install_functions.sh).

A full working example: [doc/example/50_docker_module](doc/example/50_docker_module)

# Releasing and updating
## Publish snapshot

1. pyb publish upload
2. sudo pip3 install --pre ddadevops==0.7.0.devxxx --user


## Release
1. Versions nr in build.py: *.dev entfernen
1. git commit -am "release"
2. git tag [version]
3. pyb publish upload
4. git push && git push --tag
5. Versions nr in build.py: hochzählen, *.dev anfügen
7. git commit -am "version bump"
8. git push
9. sudo pip3 install ddadevops==0.7.0 --user


# License

Copyright © 2019 meissa GmbH
Licensed under the [Apache License, Version 2.0](LICENSE) (the "License")

