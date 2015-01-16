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

"""App factory."""

import json
import logging
import os

from oslo.config import cfg
import pecan
from pecan import hooks
import webob

from refstack import utils

logger = logging.getLogger(__name__)

CONF = cfg.CONF


class JSONErrorHook(hooks.PecanHook):
    """
    A pecan hook that translates webob HTTP errors into a JSON format.
    """
    def __init__(self, app_config):
        """Hook init."""
        self.debug = app_config.get('debug', False)

    def on_error(self, state, exc):
        """Request error handler."""
        if isinstance(exc, webob.exc.HTTPError):
            body = {'code': exc.status_int,
                    'title': exc.title}
            if self.debug:
                body['detail'] = str(exc)
            return webob.Response(
                body=json.dumps(body),
                status=exc.status,
                content_type='application/json'
            )
        else:
            logger.exception(exc)
            body = {'code': 500,
                    'title': 'Internal Server Error'}
            if self.debug:
                body['detail'] = str(exc)
            return webob.Response(
                body=json.dumps(body),
                status=500,
                content_type='application/json'
            )


def setup_app(config):
    """App factory."""
    app_conf = dict(config.app)

    app = pecan.make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        hooks=[JSONErrorHook(app_conf), hooks.RequestViewerHook(
            {'items': ['status', 'method', 'controller', 'path', 'body']},
            headers=False, writer=utils.LogWriter(logger, logging.DEBUG)
        )],
        **app_conf
    )

    # By default we expect path to oslo config file in environment variable
    # REFSTACK_OSLO_CONFIG (option for testing and development)
    # If it is empty we look up those config files
    # in the following directories:
    #   ~/.${project}/
    #   ~/
    #   /etc/${project}/
    #   /etc/
    default_config_files = ((os.getenv('REFSTACK_OSLO_CONFIG'), )
                            if os.getenv('REFSTACK_OSLO_CONFIG')
                            else cfg.find_config_files('refstack'))

    CONF('',
         project='refstack',
         default_config_files=default_config_files)

    CONF.log_opt_values(logger, logging.DEBUG)

    return app
