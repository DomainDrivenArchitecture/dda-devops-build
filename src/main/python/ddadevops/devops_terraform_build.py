from os import path
from json import load, dumps
from subprocess import run
from pkg_resources import *
from python_terraform import *
from .python_util import filter_none
from .devops_build import DevopsBuild, create_devops_build_config


def create_devops_terraform_build_config(stage, project_root_path, build_commons_path, module,
                                         additional_vars,
                                         build_dir_name='target',
                                         output_json_name='output.json',
                                         use_workspace=True,
                                         use_package_common_files=True,
                                         terraform_build_commons_dir_name='terraform',
                                         debug_print_terraform_command=False):
    ret = create_devops_build_config(
        stage, project_root_path, build_commons_path, module, build_dir_name)
    ret.update({'additional_vars': additional_vars,
                'output_json_name': output_json_name,
                'use_workspace': use_workspace,
                'use_package_common_files': use_package_common_files,
                'terraform_build_commons_dir_name': terraform_build_commons_dir_name,
                'debug_print_terraform_command': debug_print_terraform_command})
    return ret

class WorkaroundTerraform(Terraform):
    def apply(self, dir_or_plan=None, input=False, skip_plan=False, no_color=IsFlagged,
              **kwargs):
        """
        refer to https://terraform.io/docs/commands/apply.html
        no-color is flagged by default
        :param no_color: disable color of stdout
        :param input: disable prompt for a missing variable
        :param dir_or_plan: folder relative to working folder
        :param skip_plan: force apply without plan (default: false)
        :param kwargs: same as kwags in method 'cmd'
        :returns return_code, stdout, stderr
        """
        default = kwargs
        default['input'] = input
        default['no_color'] = no_color
        option_dict = self._generate_default_options(default)
        default['auto-approve'] = (skip_plan == True)
        args = self._generate_default_args(dir_or_plan)
        return self.cmd('apply', *args, **option_dict)

    def generate_cmd_string(self, cmd, *args, **kwargs):
        self.latest_cmd = super().generate_cmd_string(self, cmd, *args, **kwargs)
        return self.latest_cmd

    def latest_cmd(self):
        return self.latest_cmd


class DevopsTerraformBuild(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        project.build_depends_on('python-terraform')
        self.additional_vars = config['additional_vars']
        self.output_json_name = config['output_json_name']
        self.use_workspace = config['use_workspace']
        self.use_package_common_files = config['use_package_common_files']
        self.terraform_build_commons_dir_name = config['terraform_build_commons_dir_name']
        self.debug_print_terraform_command = config['debug_print_terraform_command']

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
        my_data = resource_string(__name__, "src/main/resources/terraform/" + name)
        with open(self.build_path() + '/' + name, "w") as output_file:
            output_file.write(my_data.decode(sys.stdout.encoding))

    def copy_build_resources_from_package(self):
        self.copy_build_resource_file_from_package('versions.tf')
        self.copy_build_resource_file_from_package('terraform_build_vars.tf')

    def copy_build_resources_from_dir(self):
        run('cp -f ' + self.terraform_build_commons_path() +
            '* ' + self.build_path(), shell=True)

    def initialize_build_dir(self):
        super().initialize_build_dir()
        if self.use_package_common_files:
            self.copy_build_resources_from_package()
        else:
            self.copy_build_resources_from_dir()
        run('cp *.tf ' + self.build_path(), shell=True)
        run('cp *.properties ' + self.build_path(), shell=True)
        run('cp *.tfars ' + self.build_path(), shell=True)

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
        tf.plan(capture_output=False, raise_on_error=True, var=self.project_vars())
        self.print_terraform_command(tf)

    def apply(self, auto_approve=False):
        tf = self.init_client()
        tf.apply(capture_output=False, raise_on_error=True, skip_plan=auto_approve,
            var=self.project_vars())
        self.print_terraform_command(tf)
        self.write_output(tf)

    def destroy(self, auto_approve=False):
        tf = self.init_client()
        if auto_approve:
            force=IsFlagged
        else:
            force=None
        tf.destroy(capture_output=False, raise_on_error=True, force=force, 
            var=self.project_vars())
        self.print_terraform_command(tf)

    def tf_import(self, tf_import_name, tf_import_resource,):
        tf = self.init_client()
        tf.import_cmd(tf_import_name, tf_import_resource,
                      capture_output=False, raise_on_error=True, var=self.project_vars())
        self.print_terraform_command(tf)

    def print_terraform_command(self, tf):
        if self.debug_print_terraform_command:
            output = 'cd ' + self.build_path() + ' ' + tf.latest_cmd()
            print(output)
