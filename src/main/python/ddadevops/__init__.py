"""
ddadevops provide tools to support builds combining gopass, 
terraform, dda-pallet, aws & hetzner-cloud.

"""

from .credential import gopass_credential_from_env_path, gopass_credential_from_path
from .devops_build import DevopsBuild, create_devops_build_config
from .devops_terraform_build import DevopsTerraformBuild, create_devops_terraform_build_config
from .hetzner_mixin import HetznerMixin, add_hetzner_mixin_config
from .aws_mixin import AwsMixin, add_aws_mixin_config
from .aws_mfa_mixin import AwsMfaMixin, add_aws_mfa_mixin_config
from .dda_pallet_mixin import DdaPalletMixin, add_dda_pallet_mixin_config

__version__ = "${version}"