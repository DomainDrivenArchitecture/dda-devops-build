from python_terraform import *
from .devops_terraform_build import DevopsTerraformBuild, WorkaroundTerraform


def add_aws_backend_properties_mixin_config(config, account_name):
    config.update({'AwsBackendPropertiesMixin':
                   {'account_name': account_name}})
    return config


class AwsBackendPropertiesMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        aws_mixin_config = config['AwsBackendPropertiesMixin']
        self.account_name = aws_mixin_config['account_name']

    def backend_config(self):
        return "backend." + self.account_name + "." + self.stage + ".properties"

    def project_vars(self):
        ret = super().project_vars()
        ret.update({'account_name': self.account_name})
        return ret

    def copy_build_resources_from_package(self):
        super().copy_build_resources_from_package()
        self.copy_build_resource_file_from_package('aws_provider.tf')
        self.copy_build_resource_file_from_package(
            'aws_backend_properties_vars.tf')
        self.copy_build_resource_file_from_package(
            'aws_backend_with_properties.tf')

    def init_client(self):
        tf = WorkaroundTerraform(working_dir=self.build_path())
        tf.init(backend_config=self.backend_config())
        self.print_terraform_command(tf)
        if self.use_workspace:
            try:
                tf.workspace('select', slef.stage)
                self.print_terraform_command(tf)
            except:
                tf.workspace('new', self.stage)
                self.print_terraform_command(tf)
        return tf

    def plan(self):
        tf = self.init_client()
        tf.plan(capture_output=False, raise_on_error=True,
                var=self.project_vars(),
                var_file=self.backend_config())
        self.print_terraform_command(tf)

    def apply(self, auto_approve=False):
        tf = self.init_client()
        tf.apply(capture_output=False, raise_on_error=True,
                 skip_plan=auto_approve,
                 var=self.project_vars(),
                 var_file=self.backend_config())
        self.print_terraform_command(tf)
        self.write_output(tf)

    def destroy(self, auto_approve=False):
        tf = self.init_client()
        if auto_approve:
            force = IsFlagged
        else:
            force = None
        tf.destroy(capture_output=False, raise_on_error=True,
                   force=force,
                   var=self.project_vars(),
                   var_file=self.backend_config())
        self.print_terraform_command(tf)
