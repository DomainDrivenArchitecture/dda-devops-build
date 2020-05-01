from string import Template
from subprocess import run
from .python_util import *
from .devops_build import DevopsBuild


def add_dda_simple_mixin_config(config, domain_file_name,
                                jar_file=None,
                                target_edn_name='target.edn'):
    config.update({'DdaSimpleMixin':
                   {'domain_file_name': domain_file_name,
                    'target_edn_name': target_edn_name,
                    'jar_file': jar_file,
                    'target_template':
                    """
{:existing [{:node-name "$node_name"
             :node-ip "$ipv4"}]
 :provisioning-user {:login "root"}}
""", }})
    return config


class DdaSimpleMixin(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        dda_pallet_mixin_config = config['DdaSimpleMixin']
        self.domain_file_name = dda_pallet_mixin_config['domain_file_name']
        self.target_edn_name = dda_pallet_mixin_config['target_edn_name']
        self.jar_file = dda_pallet_mixin_config['jar_file']
        if not self.jar_file:
            self.jar_file = 'target/uberjar/' + self.module + '-standalone.jar'
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
            domain_input = input_file.read()
        domain_template = Template(domain_input)
        with open(self.build_path() + '/out_' + self.domain_file_name, "w") as output_file:
            output_file.write(domain_template.substitute(substitues))

    def dda_uberjar(self, configure_switch=None):
        if configure_switch:
            cmd = ['java', '-jar', self.project_root_path + '/' + self.jar_file,
                   '--targets', self.build_path() + '/' + self.target_edn_name,
                   '--configure',
                   self.build_path() + '/out_' + self.domain_file_name]
        else:
            cmd = ['java', '-jar', self.project_root_path + '/' + self.jar_file,
                   '--targets', self.build_path() + '/' + self.target_edn_name,
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
