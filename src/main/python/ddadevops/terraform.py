from os import path
from json import load
from subprocess import run
from .meissa_build import stage, hetzner_api_key, tf_import_name, tf_import_resource, \
    build_commons_path, build_target_path
from .python_util import execute
from python_terraform import *

OUTPUT_JSON = "output.json"

def tf_copy_common(project):
    run(['cp', '-f', build_commons_path(project) + 'terraform/aws_provider.tf', \
        build_target_path(project) + 'aws_provider.tf'])
    run(['cp', '-f', build_commons_path(project) + 'terraform/variables.tf', \
        build_target_path(project) + 'variables.tf'])

def tf_plan(project):
    init(project)
    tf = Terraform(working_dir=build_target_path(project))
    tf.plan(capture_output=False, var=project_vars(project))

def tf_import(project):
    init(project)
    tf = Terraform(working_dir=build_target_path(project))
    tf.import_cmd(tf_import_name(project), tf_import_resource(project), \
        capture_output=False, var=project_vars(project))

def tf_apply(project, p_auto_approve=False):
    init(project)
    tf = Terraform(working_dir=build_target_path(project))
    tf.apply(capture_output=False, auto_approve=p_auto_approve, var=project_vars(project))
    tf_output(project)

def tf_output(project):
    init(project)
    tf = Terraform(working_dir=build_target_path(project))
    result = tf.output(json=IsFlagged)
    with open(build_target_path(project) + OUTPUT_JSON, "w") as output_file:
        output_file.write(json.dumps(result))
    
def tf_destroy(project, p_auto_approve=False):
    init(project)
    tf = Terraform(working_dir=build_target_path(project))
    tf.destroy(capture_output=False, auto_approve=p_auto_approve, var=project_vars(project))

def tf_read_output_json(project):
    with open(build_target_path(project) + OUTPUT_JSON, 'r') as f:
        return load(f)

def project_vars(project):
    my_hetzner_api_key = hetzner_api_key(project)
    my_module = project.name
    ret = {'stage' : stage(project)}
    if my_hetzner_api_key:
        ret['hetzner_api_key'] = my_hetzner_api_key
    if my_module:
        ret['module'] = my_module
    return ret

def init(project):
    tf = Terraform(working_dir=build_target_path(project))
    tf.init()
    try:
        tf.workspace('select', stage(project))
    except:
        tf.workspace('new', stage(project))
