"""
ddadevops provide tools to support builds combining gopass, 
terraform, dda-pallet, aws & hetzner-cloud.

"""

from .meissa_build import meissa_init_project, stage, module, hetzner_api_key, tf_import_name, tf_import_resource, project_dict
from .dda_pallet import dda_write_target, dda_write_domain, dda_uberjar
from .terraform import tf_copy_common, tf_plan, tf_import, tf_apply, tf_output, tf_destroy, tf_read_output_json

__version__ = "${version}"