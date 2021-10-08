from .devops_terraform_build import DevopsTerraformBuild


def add_exoscale_mixin_config(config, exoscale_api_key, exoscale_secret_key):
    config.update({'ExoscaleMixin':
                   {'exoscale_api_key': exoscale_api_key,
                    'exoscale_secret_key': exoscale_secret_key}})
    return config


class ExoscaleMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        exoscale_mixin_config = config['ExoscaleMixin']
        self.exoscale_api_key = exoscale_mixin_config['exoscale_api_key']
        self.exoscale_secret_key = exoscale_mixin_config['exoscale_secret_key']

    def project_vars(self):
        ret = super().project_vars()
        if self.exoscale_api_key:
            ret['exoscale_api_key'] = self.exoscale_api_key
        if self.exoscale_secret_key:
            ret['exoscale_secret_key'] = self.exoscale_secret_key
        return ret

    def copy_build_resources_from_package(self):
        super().copy_build_resources_from_package()
        self.copy_build_resource_file_from_package('provider_registry.tf')
        self.copy_build_resource_file_from_package('exoscale_provider.tf')
        self.copy_build_resource_file_from_package('exoscale_mixin_vars.tf')
