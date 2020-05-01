from string import Template
from subprocess import run
from .python_util import *
from .devops_build import DevopsBuild


def add_dda_tenant_mixin_config(config, tenant, application, domain_file_name):
    config.update({'DdaTenantMixin':
                   {'tenant': tenant,
                    'application': application,
                    'domain_file_name': domain_file_name,
                    'target_edn_name': 'target.edn',
                    'jar_file': 'target/meissa-tenant-server.jar',
                    'target_template':
                    """
{:existing [{:node-name "$node_name"
             :node-ip "$ipv4"}]
 :provisioning-user {:login "root"}}
""", }})
    return config


class DdaTenantMixin(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        dda_pallet_mixin_config = config['DdaTenantMixin']
        self.tenant = dda_pallet_mixin_config['tenant']
        self.application = dda_pallet_mixin_config['application']
        self.domain_file_name = dda_pallet_mixin_config['domain_file_name']
        self.target_edn_name = dda_pallet_mixin_config['target_edn_name']
        self.jar_file = dda_pallet_mixin_config['jar_file']
        self.target_template = Template(
            dda_pallet_mixin_config['target_template'])

    def initialize_build_dir(self):
        super().initialize_build_dir()
        run('cp *.edn ' + self.build_path(), shell=True)

    def dda_write_target(self, node_name, ipv4):
        with open(self.build_path() + '/' + self.target_edn_name, "w") as output_file:
            output_file.write(
                self.target_template.substitute({'ipv4': ipv4, 'node_name': node_name}))

    def dda_write_domain(self, substitues):
        with open(self.build_path() + '/' + self.domain_file_name, "r") as input_file:
            domain_input=input_file.read()
        domain_template=Template(domain_input)
        with open(self.build_path() + '/out_' + self.domain_file_name, "w") as output_file:
            output_file.write(domain_template.substitute(substitues))

    def dda_uberjar(self, configure_switch = None):
        if configure_switch:
            cmd=['java', '-jar', self.project_root_path + '/' + self.jar_file,
                   '--targets', self.build_path() + '/' + self.target_edn_name,
                   '--tenant', self.tenant, '--application', self.application,
                   '--configure',
                   self.build_path() + '/out_' + self.domain_file_name]
        else:
            cmd = ['java', '-jar', self.project_root_path + '/' + self.jar_file,
                   '--targets', self.build_path() + '/' + self.target_edn_name,
                   '--tenant', self.tenant, '--application', self.application,
                   self.build_path() + '/out_' + self.domain_file_name]
        prn_cmd = list(cmd)
        print(" ".join(prn_cmd))
        output = execute(cmd)
        print(output)
        return output

    def dda_install(self):
        return self.dda_uberjar()

    def dda_configure(self):
        return self.dda_uberjar(True)
