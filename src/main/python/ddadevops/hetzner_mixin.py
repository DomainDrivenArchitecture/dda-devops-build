from .credential import gopass_credential_from_env_path

class HetznerMixin:

    def __init__(self, project, project_root_path, build_commons_path, module, stage):
            super().__init__(self, project, project_root_path, build_commons_path, module, stage)
            self.hetzner_api_key = gopass_credential_from_env_path('HETZNER_API_KEY_PATH')

    def project_vars(self):
        ret = super().project_vars
        if self.hetzner_api_key:
            ret['hetzner_api_key'] = self.hetzner_api_key
        return ret