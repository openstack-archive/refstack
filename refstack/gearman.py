# Copyright 2014 Piston Cloud Computing, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import gear
from gear import GearmanError, TimeoutError
import json
import logging
import time
from uuid import uuid4


class RefstackGearmanClient(gear.Client):

    def __init__(self, refstack_gearman):
        """ init wrapper sets local refstack_gearman
        object with passed in one"""
        super(RefstackGearmanClient, self).__init__()
        self.__refstack_gearman = refstack_gearman


class Gearman(object):
    log = logging.getLogger("refstack.Gearman")

    def __init__(self, config):
        """ sets up connection and client object"""
        self.config = config
        self.meta_jobs = {}  # A list of meta-jobs like stop or describe

        server = config.get('gearman', 'server')
        if config.has_option('gearman', 'port'):
            port = config.get('gearman', 'port')
        else:
            port = 4730

        self.gearman = RefstackGearmanClient(self)
        self.gearman.addServer(server, port)

    def add_job(self, name, params):
        """ adds job to the gearman queue"""
        self.log.info("starting test run")
        uuid = str(uuid4().hex)

        gearman_job = gear.Job(name, json.dumps(params),
                               unique=uuid)

        if not self.is_job_registered(gearman_job.name):
            self.log.error("Job %s is not registered with Gearman" %
                           gearman_job)
            self.on_job_completed(gearman_job, 'NOT_REGISTERED')
            #return build

        try:
            self.gearman.submitJob(gearman_job)
        except GearmanError:
            self.log.exception("Unable to submit job to Gearman")
            self.on_build_completed(gearman_job, 'EXCEPTION')
            #return build

        if not gearman_job.handle:
            self.log.error("No job handle was received for %s after 30 seconds"
                           " marking as lost." %
                           gearman_job)
            self.on_build_completed(gearman_job, 'NO_HANDLE')

        self.log.debug("Received handle %s for job" % gearman_job.handle)

    def on_job_completed(self, job, result=None):
        """called when test is completed"""
        if job.unique in self.meta_jobs:
            del self.meta_jobs[job.unique]
            return result

    def is_job_registered(self, name=None):
        """ checks to see if job registered with gearman or not"""
        if not name:
            return False

        if self.function_cache_time:
            for connection in self.gearman.active_connections:
                if connection.connect_time > self.function_cache_time:
                    self.function_cache = set()
                    self.function_cache_time = 0
                    break
        if name in self.function_cache:
            self.log.debug("Function %s is registered" % name)
            return True
        if ((time.time() - self.function_cache_time) <
            self.negative_function_cache_ttl):
            self.log.debug("Function %s is not registered "
                           "(negative ttl in effect)" % name)
            return False
        self.function_cache_time = time.time()
        for connection in self.gearman.active_connections:
            try:
                req = gear.StatusAdminRequest()
                connection.sendAdminRequest(req)
            except TimeoutError:
                self.log.exception("Exception while checking functions")
                continue
            for line in req.response.split('\n'):
                parts = [x.strip() for x in line.split()]
                if not parts or parts[0] == '.':
                    continue
                self.function_cache.add(parts[0])
        if name in self.function_cache:
            self.log.debug("Function %s is registered" % name)
            return True
        self.log.debug("Function %s is not registered" % name)
        return False
