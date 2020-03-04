from python_terraform import *
from boto3 import *
from .credential import gopass_credential_from_env_path
from .python_util import execute
from .devops_terraform_build import DevopsTerraformBuild


def add_aws_mixin_config(config, account_name):
    config.update({'AwsMixin':
                   {'account_name': account_name}})
    return config


class AwsMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        aws_mixin_config = config['AwsMixin']
        self.account_name = aws_mixin_config['account_name']

    def backend_config(self):
        return "backend." + self.account_name + "." + self.stage + ".properties"

    def project_vars(self):
        ret = super().project_vars()
        ret.update({'account_name': self.account_name})
        return ret

    def init_client(self):
        tf = Terraform(working_dir=self.build_path())
        tf.init(backend_config=self.backend_config())
        if self.use_workspace:
            try:
                tf.workspace('select', slef.stage)
            except:
                tf.workspace('new', self.stage)
        return tf

    def plan(self):
        tf = self.init_client()
        tf.plan(capture_output=False, var=self.project_vars(),
                var_file=self.backend_config())

    def get_username_from_account(self, p_account_name):
        login_id = execute('cat ~/.aws/accounts | grep -A 2 "\[' + p_account_name +
                           '\]"  | grep username | awk -F= \'{print $2}\'', shell=True)
        return login_id

    def get_account_id_from_account(self, p_account_name):
        account_id = execute('cat ~/.aws/accounts | grep -A 2 "\[' + p_account_name +
                             '\]"  | grep account | awk -F= \'{print $2}\'', shell=True)
        return account_id

    def get_mfa(self, mfa_path='aws'):
        mfa_token = execute('mfa otp ' + mfa_path, shell=True)
        return mfa_token

    def write_aws_config(self, to_profile, key, secret):
        execute('aws configure --profile ' + to_profile +
                ' set ' + key + ' ' + secret, shell=True)

    def get_mfa_session(self, to_account_suffix='dev', role='kauf_developer',
                        toke=None):
        prefix = 'breuninger-'
        from_account_name = 'breuninger-iam'
        from_account_id = self.get_account_id_from_account(from_account_name)
        to_account_name = prefix + to_account_suffix
        to_account_id = self.get_account_id_from_account(to_account_name)
        login_id = self.get_username_from_account(from_account_name)
        mfa_token = self.get_mfa()
        ses = Session(profile_name=from_account_name)
        sts_client = ses.client('sts')
        response = sts_client.assume_role(
            RoleArn='arn:aws:iam::' + to_account_id + ':role/' + role,
            RoleSessionName=to_account_id + '-' + to_account_suffix + '-' + role,
            SerialNumber='arn:aws:iam::' + from_account_id + ':mfa/' + login_id,
            TokenCode=mfa_token
        )

        self.write_aws_config(to_account_name, 'aws_access_key_id',
                              response['Credentials']['AccessKeyId'])
        self.write_aws_config(to_account_name, 'aws_secret_access_key',
                              response['Credentials']['SecretAccessKey'])
        self.write_aws_config(to_account_name, 'aws_session_token',
                              response['Credentials']['SessionToken'])
        print('got token')
