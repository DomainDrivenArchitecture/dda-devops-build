from subprocess import check_output, call, Popen, PIPE
import sys
import string

TARGET = 'target.edn'
TEMPLATE_TARGET_CONTENT = string.Template("""
{:existing [{:node-name "k8s"
             :node-ip "$ip"}]
 :provisioning-user {:login "root"}}
""")

def write_target(ip):
    with open(TARGET, "w") as output_file:
        output_file.write(TEMPLATE_TARGET_CONTENT.substitute({'ip' : ip}))

def uberjar(tenant, application, spec):
    cmd = ['java', '-jar', '../../../target/meissa-tenant-server.jar', '--targets', TARGET, 
           '--tenant', tenant, '--application', application, spec]
    prn_cmd=list(cmd)
    print(" ".join(prn_cmd))
    if sys.version_info.major == 3:
        output = check_output(cmd, encoding='UTF-8')
    else:
        output = check_output(cmd)
    print(output)
    return output
