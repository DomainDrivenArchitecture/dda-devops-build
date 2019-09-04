from subprocess import check_output, call, Popen, PIPE
import os
import sys
import json
import meissa_build

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

def copy_common(base_path):
    call(['cp', '-f', base_path + '00_build_common/terraform/gitignore_on_target', '.gitignore'])
    call(['cp', '-f', base_path + '00_build_common/terraform/aws_provider.tf', 'aws_provider.tf'])
    call(['cp', '-f', base_path + '00_build_common/terraform/variables.tf', 'variables.tf'])

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
    if sys.version_info.major == 3:
        output = check_output(tf_cmd, encoding='UTF-8')
    else:
        output = check_output(tf_cmd)
    print(output)
    return output

def init(project):
    terraform(TF_INIT_CMD) 
    try:
        terraform(TF_SELECT_WORKSPACE_CMD, None, [meissa_build.stage(project)])
    except:
        terraform(TF_NEW_WORKSPACE_CMD, None, [meissa_build.stage(project)])

def write_output():
    output = terraform(TF_OUTPUT_CMD)
    with open(OUTPUT_JSON, "w") as output_file:
        output_file.write(output)

def read_output_json():
    with open(OUTPUT_JSON, 'r') as f:
        return json.load(f)

def get_hetzner_api_key_as_var(project):
    hetzner_api_key = meissa_build.hetzner_api_key(project)
    ret = []
    if hetzner_api_key:
        ret.extend(['-var', 'hetzner_api_key=' + hetzner_api_key])
    return ret

def plan_apply(project):
    init(project)
    terraform(TF_PLAN_CMD, get_hetzner_api_key_as_var(project), ['-out', APPLY_PLAN])

def tf_import(project):
    init(project)
    terraform(TF_IMPORT_CMD, get_hetzner_api_key_as_var(project), [meissa_build.tf_import_name(project), meissa_build.tf_import_resource(project)])

def plan_destroy(project):
    init(project)
    terraform(TF_PLAN_CMD, get_hetzner_api_key_as_var(project), ['-destroy'])

def apply(project, auto_approve=None):
    if not os.path.isfile(APPLY_PLAN):
        plan_apply(project)
    else:
        init(project)
    cmd = []
    if auto_approve:
        cmd.extend(['-auto-approve', '-input=false'])
    cmd.append(APPLY_PLAN)
    terraform(TF_APPLY_CMD, None, cmd)
    write_output()
    
def destroy(project, auto_approve=None):
    cmd = []
    if auto_approve:
        cmd.extend(['-auto-approve', '-input=false'])
    terraform(TF_DESTROY_CMD, get_hetzner_api_key_as_var(project), cmd)
    write_output()
