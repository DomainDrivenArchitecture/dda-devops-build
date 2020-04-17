from .python_util import *
import deprecation

@deprecation.deprecated(deprecated_in="0.5.0", removed_in="1.0",
                        details='use gopass_password_from_path(os.environ.get(env_var, None)) instead')
def gopass_credential_from_env_path (env_var):
    env_path = os.environ.get(env_var, None)
    return gopass_password_from_path(env_path)

@deprecation.deprecated(deprecated_in="0.5.0", removed_in="1.0",
                        details='use gopass_password_from_path(path) instead')
def gopass_credential_from_path (path):
    return gopass_password_from_path(path)


def gopass_field_from_path (path, field):
    credential = None
    if path and field:
        print('get field for: ' + path + ', ' + field)
        credential = execute(['gopass', 'show', path, field])
    return credential

def gopass_password_from_path (path):
    credential = None
    if path:
        print('get password for: ' + path)
        credential = execute(['gopass', 'show', '--password', path])
    return credential

