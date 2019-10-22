from os import path
from json import load
from subprocess import call
from .meissa_build import stage, hetzner_api_key, tf_import_name, tf_import_resource
from .python_util import execute
from python_terraform import *

APPLY_PLAN = "proposed_apply.plan"
DESTROY_PLAN = "proposed_destroy.plan"
OUTPUT_JSON = "output.json"

TF_INIT_CMD = ['init']
TF_SELECT_WORKSPACE_CMD = ['workspace', 'select']
TF_NEW_WORKSPACE_CMD = ['workspace', 'new']
TF_OUTPUT_CMD = ['output', '-json']
TF_PLAN_CMD = ['plan']
TF_IMPORT_CMD = ['import']
TF_APPLY_CMD = ['apply']
TF_DESTROY_CMD = ['destroy']

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
    terraform(TF_IMPORT_CMD, get_hetzner_api_key_as_var(project), [tf_import_name(project), tf_import_resource(project)])

def tf_apply(project, auto_approve=None):
    init(project)
    tf = Terraform(working_dir='.')
    if auto_approve:
        tf.apply(capture_output=False, auto_approve=True, var=get_hetzner_api_key_as_dict(project))
    else:
        tf.apply(capture_output=False, var=get_hetzner_api_key_as_dict(project))
    tf_output(project)

def tf_output(project):
    tf = Terraform(working_dir='.')
    result = tf.output(json=IsFlagged)
    with open(OUTPUT_JSON, "w") as output_file:
        output_file.write(json.dumps(result))
    
def tf_destroy(project, auto_approve=None):
    tf = Terraform(working_dir='.')
    if auto_approve:
        tf.destroy(capture_output=False, auto_approve=True, var=get_hetzner_api_key_as_dict(project))
    else:
        tf.destroy(capture_output=False, var=get_hetzner_api_key_as_dict(project))

def tf_read_output_json():
    with open(OUTPUT_JSON, 'r') as f:
        return load(f)

def terraform(cmd, credentials=None, options=None):
    tf_cmd = ['terraform']
    tf_cmd.extend(cmd)
    prn_cmd=list(tf_cmd)
    if credentials:
        tf_cmd.extend(credentials)
        prn_cmd.extend([credentials[0], credentials[1].split('=', 1)[0] + '=xxx'])
    if options:
        tf_cmd.extend(options)
        prn_cmd.extend(options)
    print(" ".join(prn_cmd))
    output = execute(tf_cmd)
    return output

def init(project):
    tf = Terraform(working_dir='.')
    tf.init()
    try:
        tf.workspace('select', stage(project))
    except:
        tf.workspace('new', stage(project))

def get_hetzner_api_key_as_var(project):
    my_hetzner_api_key = hetzner_api_key(project)
    ret = []
    if my_hetzner_api_key:
        ret.extend(['-var', 'hetzner_api_key=' + my_hetzner_api_key])
    return ret

def get_hetzner_api_key_as_dict(project):
    my_hetzner_api_key = hetzner_api_key(project)
    ret = {}
    if my_hetzner_api_key:
        ret['hetzner_api_key'] = my_hetzner_api_key
    return ret

