from .credential import gopass_credential_from_env_path
from .devops_terraform_build import DevopsTerraformBuild


def add_hetzner_mixin_config(config):
    config.update({'HetznerMixin':
                   {'HETZNER_API_KEY_PATH_ENVIRONMENT': 'HETZNER_API_KEY_PATH'}})
    return config


class HetznerMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(self, project, config)
        hetzner_mixin_config = config['HetznerMixin']
        self.hetzner_api_key = gopass_credential_from_env_path(
            hetzner_mixin_config['HETZNER_API_KEY_PATH_ENVIRONMENT'])

    def project_vars(self):
        ret = super().project_vars
        if self.hetzner_api_key:
            ret['hetzner_api_key'] = self.hetzner_api_key
        return ret
