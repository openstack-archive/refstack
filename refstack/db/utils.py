# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
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

"""Utilities for database."""
from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class PluggableBackend(object):
    """A pluggable backend loaded lazily based on some value."""

    def __init__(self, pivot, **backends):
        """Init."""
        self.__backends = backends
        self.__pivot = pivot
        self.__backend = None

    def __get_backend(self):
        """Get backend."""
        if not self.__backend:
            backend_name = CONF[self.__pivot]
            if backend_name not in self.__backends:  # pragma: no cover
                raise Exception('Invalid backend: %s' % backend_name)

            backend = self.__backends[backend_name]
            if isinstance(backend, tuple):  # pragma: no cover
                name = backend[0]
                fromlist = backend[1]
            else:
                name = backend
                fromlist = backend

            self.__backend = __import__(name, None, None, fromlist)
            LOG.debug('backend %s', self.__backend)
        return self.__backend

    def __getattr__(self, key):
        """Proxy interface to backend."""
        backend = self.__get_backend()
        return getattr(backend, key)
