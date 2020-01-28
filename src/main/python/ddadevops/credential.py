from subprocess import check_output, call
import os
import sys

def gopass_credential_from_env_path (env_var):
    env_path = os.environ.get(env_var, None)
    return gopass_credential_from_path(env_path)

def gopass_credential_from_path (path):
    credential = None

    if path:
        print('get credential for: ' + path)
        if sys.version_info.major == 3:
            credential = check_output(['gopass', path], encoding='UTF-8')
        else:
            credential = check_output(['gopass', path])

    return credential

