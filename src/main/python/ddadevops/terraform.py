from os import path
from json import load
from subprocess import call
from .meissa_build import stage, hetzner_api_key, tf_import_name, tf_import_resource
from .python_util import execute
from python_terraform import *

OUTPUT_JSON = "output.json"

def tf_copy_common(base_path):
    call(['cp', '-f', base_path + '00_build_common/terraform/gitignore_on_target', '.gitignore'])
    call(['cp', '-f', base_path + '00_build_common/terraform/aws_provider.tf', 'aws_provider.tf'])
    call(['cp', '-f', base_path + '00_build_common/terraform/variables.tf', 'variables.tf'])

def tf_plan(project):
    init(project)
    tf = Terraform(working_dir='.')
    tf.plan(capture_output=False, var=get_hetzner_api_key_as_dict(project))

def tf_import(project):
    init(project)
    tf = Terraform(working_dir='.')
    tf.import_cmd(capture_output=False, var=get_hetzner_api_key_as_dict(project), tf_import_name(project), tf_import_resource(project))

def tf_apply(project, p_auto_approve=False):
    init(project)
    tf = Terraform(working_dir='.')
    tf.apply(capture_output=False, auto_approve=p_auto_approve, var=get_hetzner_api_key_as_dict(project))
    tf_output(project)

def tf_output(project):
    tf = Terraform(working_dir='.')
    result = tf.output(json=IsFlagged)
    with open(OUTPUT_JSON, "w") as output_file:
        output_file.write(json.dumps(result))
    
def tf_destroy(project, p_auto_approve=False):
    tf = Terraform(working_dir='.')
    tf.destroy(capture_output=False, auto_approve=p_auto_approve, var=get_hetzner_api_key_as_dict(project))

def tf_read_output_json():
    with open(OUTPUT_JSON, 'r') as f:
        return load(f)

def init(project):
    tf = Terraform(working_dir='.')
    tf.init()
    try:
        tf.workspace('select', stage(project))
    except:
        tf.workspace('new', stage(project))

def get_hetzner_api_key_as_dict(project):
    my_hetzner_api_key = hetzner_api_key(project)
    ret = {}
    if my_hetzner_api_key:
        ret['hetzner_api_key'] = my_hetzner_api_key
    return ret

