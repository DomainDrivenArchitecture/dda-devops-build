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
                                         additional_tfvar_files=[]):
    ret = create_devops_build_config(
        stage, project_root_path, module, build_dir_name)
    ret.update({'additional_vars': additional_vars,
                'output_json_name': output_json_name,
                'use_workspace': use_workspace,
                'use_package_common_files': use_package_common_files,
                'build_commons_path': build_commons_path,
                'terraform_build_commons_dir_name': terraform_build_commons_dir_name,
                'debug_print_terraform_command': debug_print_terraform_command,
                'additional_tfvar_files': additional_tfvar_files})
    return ret


class WorkaroundTerraform(Terraform):
    def __init__(self, working_dir=None,
                 targets=None,
                 state=None,
                 variables=None,
                 parallelism=None,
                 var_file=None,
                 terraform_bin_path=None,
                 is_env_vars_included=True,
                 ):
        super().__init__(working_dir, targets, state, variables, parallelism,
                         var_file,  terraform_bin_path, is_env_vars_included)
        self.latest_cmd = ''

    def generate_cmd_string(self, cmd, *args, **kwargs):
        result = super().generate_cmd_string(cmd, *args, **kwargs)
        self.latest_cmd = ' '.join(result)
        return result


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
        tf = WorkaroundTerraform(working_dir=self.build_path())
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
            output_file.write(json.dumps(result))

    def read_output_json(self):
        with open(self.build_path() + self.output_json_name, 'r') as f:
            return load(f)

    def plan(self):
        tf = self.init_client()
        tf.plan(capture_output=False, raise_on_error=False,
                var=self.project_vars(),
                var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)

    def apply(self, auto_approve=False):
        tf = self.init_client()
        tf.apply(capture_output=False, raise_on_error=True,
                 skip_plan=auto_approve,
                 var=self.project_vars(),
                 var_file=self.additional_tfvar_files)
        self.write_output(tf)
        self.post_build()
        self.print_terraform_command(tf)

    def destroy(self, auto_approve=False):
        tf = self.init_client()
        if auto_approve:
            force = IsFlagged
        else:
            force = None
        tf.destroy(capture_output=False, raise_on_error=True,
                   force=force,
                   var=self.project_vars(),
                   var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)

    def tf_import(self, tf_import_name, tf_import_resource,):
        tf = self.init_client()
        tf.import_cmd(tf_import_name, tf_import_resource,
                      capture_output=False, raise_on_error=True,
                      var=self.project_vars(),
                      var_file=self.additional_tfvar_files)
        self.post_build()
        self.print_terraform_command(tf)

    def print_terraform_command(self, tf):
        if self.debug_print_terraform_command:
            output = 'cd ' + self.build_path() + ' && ' + tf.latest_cmd
            print(output)
