from boto3 import *
from .python_util import execute
from .aws_backend_properties_mixin import AwsBackendPropertiesMixin


def add_aws_mfa_mixin_config(config, account_id, region,
                             mfa_role='developer', mfa_account_prefix='', 
                             mfa_login_account_suffix='main'):
    config.update({'AwsMfaMixin':
                   {'account_id': account_id,
                    'region': region,
                    'mfa_role': mfa_role,
                    'mfa_account_prefix': mfa_account_prefix,
                    'mfa_login_account_suffix': mfa_login_account_suffix}})
    return config


class AwsMfaMixin(AwsBackendPropertiesMixin):

    def __init__(self, project, config):
        super().__init__(project, config)
        project.build_depends_on('boto3')
        project.build_depends_on('mfa')
        aws_mfa_mixin_config = config['AwsMfaMixin']
        self.account_id = aws_mfa_mixin_config['account_id']
        self.region = aws_mfa_mixin_config['region']
        self.mfa_role = aws_mfa_mixin_config['mfa_role']
        self.mfa_account_prefix = aws_mfa_mixin_config['mfa_account_prefix']
        self.mfa_login_account_suffix = aws_mfa_mixin_config['mfa_login_account_suffix']

    def project_vars(self):
        ret = super().project_vars()
        ret.update({'account_name': self.account_name,
                    'account_id': self.account_id,
                    'region': self.region,
                    'mfa_role': self.mfa_role,
                    'mfa_account_prefix': self.mfa_account_prefix,
                    'mfa_login_account_suffix': self.mfa_login_account_suffix})
        return ret

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

    def get_mfa_session(self, toke=None):
        from_account_name = self.mfa_account_prefix + self.mfa_login_account_suffix
        from_account_id = self.get_account_id_from_account(from_account_name)
        to_account_name = self.mfa_account_prefix + self.account_name
        to_account_id = self.get_account_id_from_account(to_account_name)
        login_id = self.get_username_from_account(from_account_name)
        mfa_token = self.get_mfa()
        ses = Session(profile_name=from_account_name)
        sts_client = ses.client('sts')
        response = sts_client.assume_role(
            RoleArn='arn:aws:iam::' + to_account_id + ':role/' + self.mfa_role,
            RoleSessionName=to_account_id + '-' + self.account_name + '-' + self.mfa_role,
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
