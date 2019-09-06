from .python_util import *
import string


TARGET = 'target.edn'
TEMPLATE_TARGET_CONTENT = string.Template("""
{:existing [{:node-name "k8s"
             :node-ip "$ip"}]
 :provisioning-user {:login "root"}}
""")

def dda_write_target(ip):
    with open(TARGET, "w") as output_file:
        output_file.write(TEMPLATE_TARGET_CONTENT.substitute({'ip' : ip}))

def dda_uberjar(tenant, application, spec):
    cmd = ['java', '-jar', '../../../target/meissa-tenant-server.jar', '--targets', TARGET, 
           '--tenant', tenant, '--application', application, spec]
    prn_cmd=list(cmd)
    print(" ".join(prn_cmd))
    output = execute(cmd)
    print(output)
    return output
