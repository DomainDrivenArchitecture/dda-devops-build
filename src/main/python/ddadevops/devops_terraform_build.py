from os import path
from json import load
from subprocess import run
from python_terraform import *
from .devops_build import DevopsBuild, create_devops_build_config


def create_devops_terraform_build_config(stage, project_root_path, build_commons_path, module,
                                         account_name, additional_vars, tf_import_name, tf_import_resource):
    ret = create_devops_build_config(
        stage, project_root_path, build_commons_path, module)
    return ret.update({'account_name': account_name,
                       'additional_vars': additional_vars,
                       'tf_import_name': tf_import_name,
                       'tf_import_resource': tf_import_resource,
                       'terraform_build_commons_dir_name': 'terraform',
                       'output_json_name': 'output.json'})


class DevopsTerraformBuild(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(self, project, config)
        self.additional_vars = config['additional_vars']
        self.tf_import_name = config['tf_import_name']
        self.tf_import_resource = config['tf_import_resource']
        self.terraform_build_commons_dir_name = config['terraform_build_commons_dir_name']
        self.output_json_name = config['output_json_name']

    def terraform_build_commons_path(self):
        return self.build_commons_path() + '/' + self.terraform_build_commons_dir_name

    def project_vars(self):
        ret = {'stage': self.stage}
        if self.module:
            ret['module'] = self.module
        if self.additional_vars:
            ret.update(self.additional_vars)
        return ret

    def initialize_build_dir(self):
        super().initialize_build_dir()
        run('cp -f ' + self.terraform_build_commons_path +
            '* ' + self.build_path, shell=True)
        run('cp *.tf ' + self.build_path, shell=True)
        run('cp *.properties ' + self.build_path, shell=True)
        run('cp *.tfars ' + self.build_path, shell=True)
        run('cp *.edn ' + self.build_path, shell=True)

    def init_client(self):
        tf = Terraform(working_dir=self.build_path())
        tf.init()
        try:
            tf.workspace('select', slef.stage)
        except:
            tf.workspace('new', self.stage)
        return tf

    def write_output(self, tf):
        result = tf.output(json=IsFlagged)
        with open(self.build_path() + self.output_json_name, "w") as output_file:
            output_file.write(json.dumps(result))

    def read_output_json(self):
        with open(self.build_path() + self.output_json_name, 'r') as f:
            return load(f)

    def plan(self):
        tf = self.init_client()
        tf.plan(capture_output=False, var=self.project_vars)

    def apply(self, p_auto_approve=False):
        tf = self.init_client()
        tf.apply(capture_output=False, auto_approve=p_auto_approve,
                 var=self.project_vars())
        self.write_output(tf)

    def destroy(self, p_auto_approve=False):
        tf = self.init_client()
        tf.destroy(capture_output=False, auto_approve=p_auto_approve,
                   var=self.project_vars())

    def tf_import(self):
        tf = self.init_client()
        tf.import_cmd(self.tf_import_name, self.tf_import_resource,
                      capture_output=False, var=self.project_vars())
