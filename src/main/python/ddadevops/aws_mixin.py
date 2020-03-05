from python_terraform import *
from boto3 import *
from .credential import gopass_credential_from_env_path
from .python_util import execute
from .devops_terraform_build import DevopsTerraformBuild


def add_aws_mixin_config(config, account_name, account_id, region,
mfa_role='developer', mfa_account_prefix='', mfa_login_account_suffix='main'):
    config.update({'AwsMixin':
                   {'account_name': account_name,
                    'account_id': account_id,
                    'region': region, 
                    'mfa_role': mfa_role,
                    'mfa_account_prefix': mfa_account_prefix,
                    'mfa_login_account_suffix': mfa_login_account_suffix}})
    return config


class AwsMixin(DevopsTerraformBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        project.build_depends_on('boto3')
        aws_mixin_config = config['AwsMixin']
        self.account_name = aws_mixin_config['account_name']
        self.account_id = aws_mixin_config['account_id']
        self.region = aws_mixin_config['region']
        self.mfa_role = aws_mixin_config['mfa_role']
        self.mfa_account_prefix = aws_mixin_config['mfa_account_prefix']
        self.mfa_login_account_suffix = aws_mixin_config['mfa_login_account_suffix']

    def backend_config(self):
        return "backend." + self.account_name + "." + self.stage + ".properties"

    def project_vars(self):
        ret = super().project_vars()
        ret.update({'account_name': self.account_name,
                    'account_id': self.account_id,
                    'region': self.region,
                    'mfa_role': self.mfa_role,
                    'mfa_account_prefix': self.mfa_account_prefix,
                    'mfa_login_account_suffix': self.mfa_login_account_suffix})
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

    def apply(self, p_auto_approve=False):
        tf = self.init_client()
        tf.apply(capture_output=False, auto_approve=p_auto_approve,
                 var=self.project_vars(), var_file=self.backend_config())
        self.write_output(tf)

    def destroy(self, p_auto_approve=False):
        tf = self.init_client()
        tf.destroy(capture_output=False, auto_approve=p_auto_approve,
                   var=self.project_vars(), var_file=self.backend_config())

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
