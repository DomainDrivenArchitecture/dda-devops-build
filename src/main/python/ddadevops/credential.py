from subprocess import check_output, call
import os
import sys

def gopass_credential_from_env_path (env_path):
    env_path = os.environ.get(env_path, None)
    credential = None

    if env_path:
        print('get credential for: ' + env_path)
        if sys.version_info.major == 3:
            credential = check_output(['gopass', env_path], encoding='UTF-8')
        else:
            credential = check_output(['gopass', env_path])

    return credential
