from os import path
from json import load
from subprocess import run
from .devops_build import DevopsBuild
from .python_util import execute
from python_terraform import *

class DevopsTerraformBuild(DevopsBuild):

    def __init__(self, project, project_root_path, build_commons_path, module, stage, account_name, additional_vars):
        super().__init__(self, project, project_root_path, build_commons_path, module, stage)
        self.account_name = account_name
        self.additional_vars = additional_vars
        self.terraform_build_commons_dir_name= 'terraform'

    def backend_config(self):
        return "backend." + self.account_name + "." + self.stage + ".properties"

    def terraform_build_commons_path(self):
        return self.build_commons_path() + '/' + self.terraform_build_commons_dir_name

    def project_vars(self):
        ret = {'stage' : self.stage}
        if self.module:
            ret['module'] = self.module
        if self.additional_vars:
            ret.update(self.additional_vars)
        return ret

    def initialize_build_dir(self):
        super().initialize_build_dir()
        run('cp -f ' + self.terraform_build_commons_path + '* ' + self.build_path, shell=True)
        run('cp *.tf ' +  self.build_path, shell=True)
        run('cp *.properties ' + self.build_path, shell=True)
        run('cp *.tfars ' +  self.build_path, shell=True)
        run('cp *.edn ' +  self.build_path, shell=True)

    def init_client(self):
        tf = Terraform(working_dir=self.build_path())
        tf.init(backend_config=self.backend_config)
        try:
            tf.workspace('select', slef.stage)
        except:
            tf.workspace('new', self.stage)
        return tf

    def plan(self):
        tf = self.init_client()
        tf.plan(capture_output=False, var=self.project_vars, var_file=self.backend_config)



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
    # TODO: move to meissa specific part
    if my_hetzner_api_key:
        ret['hetzner_api_key'] = my_hetzner_api_key
    if my_module:
        ret['module'] = my_module
    return ret


