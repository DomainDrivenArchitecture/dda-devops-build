from subprocess import run
from .python_util import filter_none


def create_devops_build_config(stage, project_root_path, module,
                               build_dir_name='target'):
    return {'stage': stage,
            'project_root_path': project_root_path,
            'module': module,
            'build_dir_name': build_dir_name}

def get_devops_build(project):
    return project.get_property('devops_build')

class DevopsBuild:

    def __init__(self, project, config):
        #deprecate stage
        self.stage = config['stage']
        self.project_root_path = config['project_root_path']
        self.module = config['module']
        self.build_dir_name = config['build_dir_name']
        self.stack = {}
        self.project = project
        project.set_property('devops_build', self)

    def name(self):
        return self.project.name

    def build_path(self):
        mylist = [self.project_root_path,
                  self.build_dir_name,
                  self.name(),
                  self.module]
        return '/'.join(filter_none(mylist))

    def initialize_build_dir(self):
        run('rm -rf ' + self.build_path(), shell=True)
        run('mkdir -p ' + self.build_path(), shell=True)

    def put(self, key, value):
        self.stack[key] = value

    def get(self, key):
        return self.stack[key]
