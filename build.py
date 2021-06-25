#  dda_devops_build
#  Copyright 2019 meissa GmbH.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from pybuilder.core import init, use_plugin, Author

use_plugin("python.core")
use_plugin("copy_resources")
use_plugin("filter_resources")
#use_plugin("python.unittest")
#use_plugin("python.coverage")
use_plugin("python.distutils")

#use_plugin("python.install_dependencies")

default_task = "publish"

name = "ddadevops"
version = "0.12.2"
summary = "tools to support builds combining gopass, terraform, dda-pallet, aws & hetzner-cloud"
description = __doc__
authors = [Author("meissa GmbH", "buero@meissa-gmbh.de")]
url = "https://github.com/DomainDrivenArchitecture/dda-devops-build"
requires_python = ">=2.7,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,<3.9"
license = "Apache Software License"

@init
def initialize(project):
    #project.build_depends_on('mockito')
    #project.build_depends_on('unittest-xml-reporting')

    project.set_property("verbose", True)
    project.get_property("filter_resources_glob").append("main/python/ddadevops/__init__.py")
    #project.set_property("dir_source_unittest_python", "src/unittest/python")

    project.set_property("copy_resources_target", "$dir_dist/ddadevops")
    project.get_property("copy_resources_glob").append("LICENSE")
    project.get_property("copy_resources_glob").append("src/main/resources/terraform/*")
    project.get_property("copy_resources_glob").append("src/main/resources/docker/image/resources/*")
    project.include_file("ddadevops", "LICENSE")
    project.include_file("ddadevops", "src/main/resources/terraform/*")
    project.include_file("ddadevops", "src/main/resources/docker/image/resources/*")
    
    #project.set_property('distutils_upload_sign', True)
    #project.set_property('distutils_upload_sign_identity', '')
    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_description_overwrite", True)
    project.set_property("distutils_classifiers", [
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
        ])
