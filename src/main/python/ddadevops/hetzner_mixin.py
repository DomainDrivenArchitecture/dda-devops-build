from .devops_terraform_build import DevopsTerraformBuild


def add_hetzner_mixin_config(config, hetzner_api_key):
    config.update({'HetznerMixin':
                   {'hetzner_api_key': hetzner_api_key}})
    return config


class HetznerMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        hetzner_mixin_config = config['HetznerMixin']
        self.hetzner_api_key = hetzner_mixin_config['hetzner_api_key']

    def project_vars(self):
        ret = super().project_vars()
        if self.hetzner_api_key:
            ret['hetzner_api_key'] = self.hetzner_api_key
        return ret

    def copy_build_resources_from_package(self):
        super().copy_build_resources_from_package()
        self.copy_build_resource_file_from_package('hetzner_provider.tf')
        self.copy_build_resource_file_from_package('hetzner_mixin_vars.tf')
