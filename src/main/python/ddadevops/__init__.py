"""
ddadevops provide tools to support builds combining gopass, 
terraform, dda-pallet, aws & hetzner-cloud.

"""

from .credential import gopass_credential_from_env_path, gopass_credential_from_path, gopass_password_from_path, gopass_field_from_path
from .devops_build import DevopsBuild, create_devops_build_config, get_devops_build, get_tag_from_latest_commit
from .devops_terraform_build import DevopsTerraformBuild, create_devops_terraform_build_config
from .devops_docker_build import DevopsDockerBuild, create_devops_docker_build_config
from .hetzner_mixin import HetznerMixin, add_hetzner_mixin_config
from .exoscale_mixin import ExoscaleMixin, add_exoscale_mixin_config
from .aws_backend_properties_mixin import AwsBackendPropertiesMixin, add_aws_backend_properties_mixin_config
from .aws_mfa_mixin import AwsMfaMixin, add_aws_mfa_mixin_config
from .aws_rds_pg_mixin import AwsRdsPgMixin, add_aws_rds_pg_mixin_config
from .dda_tenant_mixin import DdaTenantMixin, add_dda_tenant_mixin_config
from .dda_simple_mixin import DdaSimpleMixin, add_dda_simple_mixin_config

__version__ = "${version}"