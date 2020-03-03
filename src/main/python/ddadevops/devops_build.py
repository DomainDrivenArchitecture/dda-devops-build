from .credential import gopass_credential_from_env_path
from subprocess import run

class DevopsBuild:

    def __init__(self, project, project_root_path, build_commons_path, module, stage):
        self.stage = stage
        self.project_root_path = project_root_path
        self.build_commons_path = build_commons_path
        self.module = module
        self.project = project
        self.build_dir_name = 'target'
        project.set_property("devops_build", self)
    
    def name(self):
        return self.project.get_property('name')

    def build_path(self):
        return self.project_root_path + self.build_dir_name + '/' + self.module + '/'

    def initialize_build_dir(self):
        run('rm -rf ' + self.build_path(), shell=True)
        run('mkdir -p ' +  self.build_path(), shell=True)


def tf_import_name(project):
    return project.get_property('tf_import_name')

def tf_import_resource(project):
    return project.get_property('tf_import_resource')

