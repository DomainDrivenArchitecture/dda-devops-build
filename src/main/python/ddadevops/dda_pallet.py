from .python_util import *
import string


TARGET = 'target.edn'
TEMPLATE_TARGET_CONTENT = string.Template("""
{:existing [{:node-name "k8s"
             :node-ip "$ipv4"}]
 :provisioning-user {:login "root"}}
""")

def dda_write_target(ipv4):
    with open(TARGET, "w") as output_file:
        output_file.write(TEMPLATE_TARGET_CONTENT.substitute({'ipv4' : ipv4}))

def dda_write_domain(domain_path, substitues):
    with open(domain_path, "r") as input_file:
        domain_input = input_file.read()
    domain_template = string.Template(domain_input)
    with open('out_' + domain_path, "w") as output_file:
        output_file.write(domain_template.substitute(substitues))

def dda_uberjar(tenant, application, spec):
    cmd = ['java', '-jar', '../../../target/meissa-tenant-server.jar', '--targets', TARGET, 
           '--tenant', tenant, '--application', application, spec]
    prn_cmd=list(cmd)
    print(" ".join(prn_cmd))
    output = execute(cmd)
    print(output)
    return output
