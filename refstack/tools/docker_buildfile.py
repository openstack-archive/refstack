# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from jinja2 import FileSystemLoader, Environment
import os
from refstack.utils import get_current_time


class DockerBuildFile(object):
    '''*
    Build a docker buildfile with customized parameters from a pre-defined
    docker build file template.
    '''

    test_id = None
    api_server_address = None
    tempest_code_url = None
    confJSON = None

    def build_docker_buildfile(self, output_file_with_path):

        '''*
        Build a docker build file based on a pre-defined template.

        This method assumes that the caller has already initialized all the
        needed parameters for customization.
        '''

        docker_template_dir = os.path.dirname(os.path.abspath(__file__))
        template_file_with_path = os.path.join(docker_template_dir,
                                               "docker_buildfile.template")

        values = {"THE_TIME_STAMP": get_current_time(),
                  "THE_TEST_ID": self.test_id,
                  "THE_API_SERVER_ADDRESS": self.api_server_address,
                  "THE_TEMPEST_CODE_URL": self.tempest_code_url,
                  "THE_CONF_JSON": self.confJSON
                  }

        template_filling(template_file_with_path, output_file_with_path,
                         values)


def template_filling(template_file_with_path,
                     output_file_with_path, value_dict):
    '''Filling values in a template file.'''

    outputText = ""
    if os.path.isfile(template_file_with_path):
        input_dir = os.path.dirname(os.path.abspath(template_file_with_path))
        file_name = os.path.basename(template_file_with_path)

        j2_env = Environment(loader=FileSystemLoader(input_dir),
                             trim_blocks=True)
        template = j2_env.get_template(file_name)
        outputText = template.render(value_dict)

    output_dir = os.path.dirname(os.path.abspath(output_file_with_path))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file_with_path, "wt") as fout:
        fout.write(outputText)
