from .python_util import *
from .meissa_build import build_target_path, project_root_path
from string import Template


TARGET = 'target.edn'
TEMPLATE_TARGET_CONTENT = Template("""
{:existing [{:node-name "k8s"
             :node-ip "$ipv4"}]
 :provisioning-user {:login "root"}}
""")

def dda_write_target(project, ipv4):
    with open(build_target_path(project) + TARGET, "w") as output_file:
        output_file.write(TEMPLATE_TARGET_CONTENT.substitute({'ipv4' : ipv4}))

def dda_write_domain(project, domain_file_name, substitues):
    with open(build_target_path(project) + domain_file_name, "r") as input_file:
        domain_input = input_file.read()
    domain_template = Template(domain_input)
    with open(build_target_path(project) + 'out_' + domain_file_name, "w") as output_file:
        output_file.write(domain_template.substitute(substitues))

def dda_install(project, tenant, application, domain_file_name):
    return dda_uberjar(project, tenant, application, domain_file_name)

def dda_configure(project, tenant, application, domain_file_name):
    return dda_uberjar(project, tenant, application, domain_file_name, True)

def dda_uberjar(project, tenant, application, domain_file_name, configure_switch=None):
    if configure_switch:
        cmd = ['java', '-jar', project_root_path(project) + 'target/meissa-tenant-server.jar', \
            '--targets', build_target_path(project) + TARGET, \
            '--tenant', tenant, '--application', application, \
            '--configure', \
            build_target_path(project) + 'out_' + domain_file_name]
    else:
        cmd = ['java', '-jar', project_root_path(project) + 'target/meissa-tenant-server.jar', \
            '--targets', build_target_path(project) + TARGET, \
            '--tenant', tenant, '--application', application, \
            build_target_path(project) + 'out_' + domain_file_name]
    prn_cmd=list(cmd)
    print(" ".join(prn_cmd))
    output = execute(cmd)
    print(output)
    return output
