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

from oslo_config import cfg
from oslo_log import log
from oslo_log import loggers
import pecan
from pecan import hooks
import webob

LOG = log.getLogger(__name__)

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir)

API_OPTS = [
    cfg.StrOpt('static_root',
               default='%(project_root)s/static',
               help='The directory where your static files can '
                    'be found. Pecan comes with middleware that can be used '
                    'to serve static files (like CSS and Javascript files) '
                    'during development. %(project_root)s is special variable '
                    'that point to the root directory of Refstack project. '
                    'Value of this option must contain %(project_root)s '
                    'variable. Directory with static files specified relative '
                    'the project root.'
               ),
    cfg.StrOpt('template_path',
               default='%(project_root)s/templates',
               help='Points to the directory where your template files live. '
                    '%(project_root)s is special variable that point to the '
                    'root directory of Refstack project. Value of this option '
                    'must contain %(project_root)s variable. Directory with '
                    'template files specified relative the project root.'
               ),
    cfg.BoolOpt('app_dev_mode',
                default=False,
                help='Switch Refstack app into debug mode. Helpful for '
                     'development. In debug mode static file will be served '
                     'by pecan application. Also, server responses will '
                     'contain some details with debug information.'
                ),
]

CONF = cfg.CONF

opt_group = cfg.OptGroup(name='api',
                         title='Options for the Refstack API')

CONF.register_group(opt_group)
CONF.register_opts(API_OPTS, opt_group)

log.register_options(CONF)


class JSONErrorHook(hooks.PecanHook):
    """
    A pecan hook that translates webob HTTP errors into a JSON format.
    """
    def __init__(self):
        """Hook init."""
        self.debug = CONF.api.app_dev_mode

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
            LOG.exception(exc)
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

    log.setup(CONF, 'refstack')
    CONF.log_opt_values(LOG, logging.DEBUG)

    template_path = CONF.api.template_path % {'project_root': PROJECT_ROOT}
    static_root = CONF.api.static_root % {'project_root': PROJECT_ROOT}

    app_conf = dict(config.app)
    app = pecan.make_app(
        app_conf.pop('root'),
        debug=CONF.api.app_dev_mode,
        static_root=static_root,
        template_path=template_path,
        hooks=[JSONErrorHook(), hooks.RequestViewerHook(
            {'items': ['status', 'method', 'controller', 'path', 'body']},
            headers=False, writer=loggers.WritableLogger(LOG, logging.DEBUG)
        )]
    )

    return app
