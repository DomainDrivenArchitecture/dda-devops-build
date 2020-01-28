"""
ddadevops provide tools to support builds combining gopass, 
terraform, dda-pallet, aws & hetzner-cloud.

"""

from .build import init_project, stage, name, module, \
    project_root_path, build_commons_path, build_target_path, \
    initialize_target, tf_import_name, tf_import_resource
from .meissa_build import meissa_init_project, hetzner_api_key
from .credential import gopass_credential_from_env_path, gopass_credential_from_path
from .dda_pallet import dda_write_target, dda_write_domain, dda_install, dda_configure
from .terraform import tf_copy_common, tf_plan, tf_import, tf_apply, tf_output, tf_destroy, \
    tf_read_output_json

__version__ = "${version}"