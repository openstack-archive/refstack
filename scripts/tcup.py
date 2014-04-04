#!/usr/bin/env python
#
# Copyright (c) 2014 Dell Computer, Inc. All Rights Reserved.
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
#

# This file creates and runs Tempest in a Docker Container
import commands
import logging
import os
import re
import sys

if __name__ == "__main__":

    # Reference Information
    DOCKER_FILE_SOURCE = os.path.join("scripts", "tcup")
    DOCKER_FILE_URL = "https://raw.githubusercontent.com/stackforge/" \
        "refstack/master/scripts/tcup/Dockerfile"
    REFSTACK_API_ADDRESS = "http://refstack.org/replace_with_correct_url"
    IGNORED_ENV_VARS = {"LS_COLORS", "HOME", "PATH", "PWD", "OLDPWD",
                        "LESSCLOSE", "SSH_CONNECTION"}
    REQUIRED_ENV_VARS = {'OS_PASSWORD', 'OS_USERNAME', 'OS_AUTH_URL'}

    # debugging?
    debug = ((len(sys.argv) > 1 and sys.argv[1] == "--debug")
             or os.environ.get("DEBUG"))

    # Setup the logger
    LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
    logger = logging.getLogger("TCUP")
    console_log_handle = logging.StreamHandler()
    console_log_handle.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_log_handle)
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Starting in DEBUG mode.")
    else:
        logger.setLevel(logging.INFO)

    # Confirm you've sourced their openrc credentials already
    for env_var in REQUIRED_ENV_VARS:
        if not os.environ.get(env_var):
            exp = 'Env Variable "%s" Missing: ' \
                  'You may need to "source openrc.sh".' % (env_var)
            raise Exception(exp)

    # build the container
    logger.info("Downloading & Building TCUP Image...(may take a long time)")
    if os.path.isfile(DOCKER_FILE_SOURCE + "/Dockerfile"):
        docker_builder = DOCKER_FILE_SOURCE
    else:
        docker_builder = DOCKER_FILE_URL
    logger.info("Executing: `docker build %s`" % (docker_builder))
    build_output = commands.getoutput("docker build %s" % (docker_builder))

    # provide friendly output progress message
    search_for = "Successfully built ([0-9a-f]{12})"
    try:
        image = re.search(search_for, build_output).group(1)
    except re.error:
        exp = "ERROR building TCUP container. Details: %s" % (build_output)
        raise Exception(exp)
    logger.info("TCUP Built Docker Image ID: %s" % (image))

    # collect environment variables to pass, we don't want all of them
    user_env_vars = dict(os.environ)
    for env_var in IGNORED_ENV_VARS:
        user_env_vars.pop(env_var, None)

    # test specific configuration
    if not os.environ.get('TEST_ID'):
        user_env_vars["test_id"] = "1000"  # TODO: generated good value!

    if not os.environ.get('API_SERVER_ADDRESS'):
        user_env_vars["api_addr"] = REFSTACK_API_ADDRESS

    # create the docker run command line
    docker_run = "docker run -d -i"
    for env_var in user_env_vars:
        docker_run += ' -e "%s=%s"' % (env_var, user_env_vars[env_var])
    if debug:
        docker_run += " -v `pwd`:/dev"
    docker_run += ' -t %s' % (image)
    if debug:
        docker_run += " /bin/bash"
        logger.info("Debug mode does not start tests! \
                    You must run `refstack/refstack/tools/execute_test.py \
                    --tempest-home /tempest` to complete processing")
    else:
        docker_run += " cd refstack; refstack/tools/execute_test.py" \
                      " --tempest-home /tempest" \
                      " --callback ${api_addr} ${test_id}"
    if debug:
        docker_run_log_output = docker_run
    else:
        # normally we redact the password
        clear_password = "OS_PASSWORD=%s" % user_env_vars['OS_PASSWORD']
        docker_run_log_output = docker_run.replace(clear_password,
                                                   "OS_PASSWORD=!REDACTED!")
    logger.info("Executing: '%s'" % (docker_run_log_output))

    # start the container and advise the user about how to attach
    docker_output = commands.getoutput(docker_run)
    logger.debug(docker_output)
    logger.info("""You can monitor the TCUP results using the command
                'docker attach %s'
                (hint: you may need to press [enter])"""
                % docker_output[0:12])
