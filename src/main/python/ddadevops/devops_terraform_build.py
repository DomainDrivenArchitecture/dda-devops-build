from os import path
from json import load, dumps
from subprocess import run
from pkg_resources import *
from python_terraform import *
from .python_util import filter_none
from .devops_build import DevopsBuild, create_devops_build_config
import sys


def create_devops_terraform_build_config(stage,
                                         project_root_path,
                                         module,
                                         additional_vars,
                                         build_dir_name='target',
                                         output_json_name='output.json',
                                         use_workspace=True,
                                         use_package_common_files=True,
                                         build_commons_path=None,
                                         terraform_build_commons_dir_name='terraform',
                                         debug_print_terraform_command=False,
                                         additional_tfvar_files=[],
                                         terraform_version=0.15):
    ret = create_devops_build_config(
        stage, project_root_path, module, build_dir_name)
    ret.update({'additional_vars': additional_vars,
                'output_json_name': output_json_name,
                'use_workspace': use_workspace,
                'use_package_common_files': use_package_common_files,
                'build_commons_path': build_commons_path,
                'terraform_build_commons_dir_name': terraform_build_commons_dir_name,
                'debug_print_terraform_command': debug_print_terraform_command,
                'additional_tfvar_files': additional_tfvar_files,
                'terraform_version': terraform_version})
    return ret

class DevopsTerraformBuild(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        project.build_depends_on('python-terraform')
        self.additional_vars = config['additional_vars']
        self.output_json_name = config['output_json_name']
        self.use_workspace = config['use_workspace']
        self.use_package_common_files = config['use_package_common_files']
        self.build_commons_path = config['build_commons_path']
        self.terraform_build_commons_dir_name = config['terraform_build_commons_dir_name']
        self.debug_print_terraform_command = config['debug_print_terraform_command']
        self.additional_tfvar_files = config['additional_tfvar_files']
        self.terraform_version = config['terraform_version']

    def terraform_build_commons_path(self):
        mylist = [self.build_commons_path,
                  self.terraform_build_commons_dir_name]
        return '/'.join(filter_none(mylist)) + '/'

    def project_vars(self):
        ret = {'stage': self.stage}
        if self.module:
            ret['module'] = self.module
        if self.additional_vars:
            ret.update(self.additional_vars)
        return ret

    def copy_build_resource_file_from_package(self, name):
        my_data = resource_string(
            __name__, "src/main/resources/terraform/" + name)
        with open(self.build_path() + '/' + name, "w") as output_file:
            output_file.write(my_data.decode(sys.stdout.encoding))

    def copy_build_resources_from_package(self):
        self.copy_build_resource_file_from_package('versions.tf')
        self.copy_build_resource_file_from_package('terraform_build_vars.tf')

    def copy_build_resources_from_dir(self):
        run('cp -f ' + self.terraform_build_commons_path() +
            '* ' + self.build_path(), shell=True)

    def copy_local_state(self):
        run('cp terraform.tfstate '  + self.build_path(), shell=True)

    def rescue_local_state(self):
        run('cp ' + self.build_path() + '/terraform.tfstate .', shell=True)

    def initialize_build_dir(self):
        super().initialize_build_dir()
        if self.use_package_common_files:
            self.copy_build_resources_from_package()
        else:
            self.copy_build_resources_from_dir()
        self.copy_local_state()
        run('cp *.tf ' + self.build_path(), shell=True)
        run('cp *.properties ' + self.build_path(), shell=True)       
        run('cp *.tfvars ' + self.build_path(), shell=True)
        run('cp -r scripts ' + self.build_path(), shell=True)

    def post_build(self):
        self.rescue_local_state()
        
    def init_client(self):
        tf = Terraform(working_dir=self.build_path())
        tf.init()
        self.print_terraform_command(tf)
        if self.use_workspace:
            try:
                tf.workspace('select', self.stage)
                self.print_terraform_command(tf)
            except:
                tf.workspace('new', self.stage)
                self.print_terraform_command(tf)
        return tf

    def write_output(self, tf):
        result = tf.output(json=IsFlagged)
        self.print_terraform_command(tf)
        with open(self.build_path() + self.output_json_name, "w") as output_file:
            output_file.write(dumps(result))

    def read_output_json(self):
        with open(self.build_path() + self.output_json_name, 'r') as f:
            return load(f)

    def plan(self):
        tf = self.init_client()
        return_code, stdout, stderr = tf.plan(detailed_exitcode=None, capture_output=False, raise_on_error=False,
                var=self.project_vars(),
                var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code > 0):
            raise Exception(return_code, "terraform error:", stderr)

    def plan_fail_on_diff(self):
        tf = self.init_client()
        return_code, stdout, stderr = tf.plan(detailed_exitcode=IsFlagged, capture_output=False, raise_on_error=False,
                var=self.project_vars(),
                var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code != 0 and return_code != 2):
            raise Exception(return_code, "terraform error:", stderr)
        if (return_code == 2):
            raise Exception(return_code, "diff in config found:", stderr)

    def apply(self, auto_approve=False):
        tf = self.init_client()
        if auto_approve:
            auto_approve_flag = IsFlagged
        else:
            auto_approve_flag = None
        if self.terraform_version >= 1.0:
            return_code, stdout, stderr = tf.apply(capture_output=False, raise_on_error=True,
                    auto_approve=auto_approve_flag,
                    var=self.project_vars(),
                    var_file=self.additional_tfvar_files)
        else:
            return_code, stdout, stderr = tf.apply(capture_output=False, raise_on_error=True,
                    skip_plan=auto_approve,
                    var=self.project_vars(),
                    var_file=self.additional_tfvar_files)
        self.write_output(tf)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code > 0):
            raise Exception(return_code, "terraform error:", stderr)

    def refresh(self, auto_approve=True):
        tf = self.init_client()
        return_code, stdout, stderr = tf.refresh(
                var=self.project_vars(),
                var_file=self.additional_tfvar_files)
        self.write_output(tf)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code > 0):
            raise Exception(return_code, "terraform error:", stderr)

    def destroy(self, auto_approve=False):
        tf = self.init_client()
        if auto_approve:
            auto_approve_flag = IsFlagged
        else:
            auto_approve_flag = None
        if self.terraform_version >= 1.0:
            return_code, stdout, stderr = tf.destroy(capture_output=False, raise_on_error=True,
                    auto_approve=auto_approve_flag,
                    var=self.project_vars(),
                    var_file=self.additional_tfvar_files)
        else:
            return_code, stdout, stderr = tf.destroy(capture_output=False, raise_on_error=True,
                    force=auto_approve_flag,
                    var=self.project_vars(),
                    var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code > 0):
            raise Exception(return_code, "terraform error:", stderr)

    def tf_import(self, tf_import_name, tf_import_resource,):
        tf = self.init_client()
        return_code, stdout, stderr = tf.import_cmd(tf_import_name, tf_import_resource,
                      capture_output=False, raise_on_error=True,
                      var=self.project_vars(),
                      var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)
        if (return_code > 0):
            raise Exception(return_code, "terraform error:", stderr)

    def print_terraform_command(self, tf):
        if self.debug_print_terraform_command:
            output = 'cd ' + self.build_path() + ' && ' + tf.latest_cmd()
            print(output)
