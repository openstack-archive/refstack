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

from beaker.middleware import SessionMiddleware
from oslo_config import cfg
from oslo_log import log
import pecan
import six
import webob

from refstack.api import exceptions as api_exc
from refstack.api import utils as api_utils
from refstack.api import constants as const
from refstack import db

LOG = log.getLogger(__name__)

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir)
UI_OPTS = [
    cfg.StrOpt('ui_url',
               default='https://refstack.openstack.org',
               help='Url of user interface for RefStack. Need for redirects '
                    'after sign in and sign out.'
               ),
]

API_OPTS = [
    cfg.StrOpt('api_url',
               default='https://refstack.openstack.org/api',
               help='Url of public RefStack API.'
               ),
    cfg.StrOpt('static_root',
               default='refstack-ui/app',
               help='The directory where your static files can be found. '
                    'Pecan  comes with middleware that can be used to serve '
                    'static files (like CSS and Javascript files) during '
                    'development. Here, a special variable %(project_root)s '
                    'can be used to point to the root directory of the '
                    'Refstack project\'s module, so paths can be specified '
                    'relative to that.'
               ),
    cfg.StrOpt('template_path',
               default='refstack-ui/app',
               help='Points to the directory where your template files live. '
                    'Here, a special variable %(project_root)s can be used to '
                    'point to the root directory of the Refstack project\'s '
                    'main module, so paths can be specified relative to that.'
               ),
    cfg.ListOpt('allowed_cors_origins',
                default=[],
                help='List of sites allowed cross-site resource access. If '
                     'this is empty, only same-origin requests are allowed.'
                ),
    cfg.BoolOpt('app_dev_mode',
                default=False,
                help='Switch Refstack app into debug mode. Helpful for '
                     'development. In debug mode static file will be served '
                     'by pecan application. Also, server responses will '
                     'contain some details with debug information.'
                ),
    cfg.StrOpt('test_results_url',
               default='/#/results/%s',
               help='Template for test result url.'
               ),
    cfg.StrOpt('github_api_capabilities_url',
               default='https://api.github.com'
                       '/repos/openstack/defcore/contents',
               help='The GitHub API URL of the repository and location of '
                    'the DefCore capability files. This URL is used to get '
                    'a listing of all capability files.'
               ),
    cfg.StrOpt('github_raw_base_url',
               default='https://raw.githubusercontent.com'
                       '/openstack/defcore/master/',
               help='This is the base URL that is used for retrieving '
                    'specific capability files. Capability file names will '
                    'be appended to this URL to get the contents of that file.'
               )
]

CONF = cfg.CONF

opt_group = cfg.OptGroup(name='api',
                         title='Options for the Refstack API')

CONF.register_opts(UI_OPTS)

CONF.register_group(opt_group)
CONF.register_opts(API_OPTS, opt_group)

log.register_options(CONF)


class JSONErrorHook(pecan.hooks.PecanHook):
    """A pecan hook that translates webob HTTP errors into a JSON format."""

    def __init__(self):
        """Hook init."""
        self.debug = CONF.api.app_dev_mode

    def on_error(self, state, exc):
        """Request error handler."""
        if isinstance(exc, webob.exc.HTTPRedirection):
            return
        elif isinstance(exc, webob.exc.HTTPError):
            return webob.Response(
                body=json.dumps({'code': exc.status_int,
                                 'title': exc.title,
                                 'detail': exc.detail}),
                status=exc.status_int,
                content_type='application/json'
            )
        title = None
        if isinstance(exc, api_exc.ValidationError):
            status_code = 400
        elif isinstance(exc, api_exc.ParseInputsError):
            status_code = 400
        elif isinstance(exc, db.NotFound):
            status_code = 404
        elif isinstance(exc, db.Duplication):
            status_code = 409
        else:
            LOG.exception(exc)
            status_code = 500
            title = 'Internal Server Error'

        body = {'title': title or exc.args[0], 'code': status_code}
        if self.debug:
            body['detail'] = six.text_type(exc)
        return webob.Response(
            body=json.dumps(body),
            status=status_code,
            content_type='application/json'
        )


class WritableLogger(object):
    """A thin wrapper that responds to `write` and logs."""

    def __init__(self, logger, level):
        """Init the WritableLogger by getting logger and log level."""
        self.logger = logger
        self.level = level

    def write(self, msg):
        """Invoke logger with log level and message."""
        self.logger.log(self.level, msg.rstrip())


class CORSHook(pecan.hooks.PecanHook):
    """A pecan hook that handles Cross-Origin Resource Sharing."""

    def __init__(self):
        """Init the hook by getting the allowed origins."""
        self.allowed_origins = getattr(CONF.api, 'allowed_cors_origins', [])

    def after(self, state):
        """Add CORS headers to the response.

        If the request's origin is in the list of allowed origins, add the
        CORS headers to the response.
        """
        origin = state.request.headers.get('Origin', None)
        if origin in self.allowed_origins:
            state.response.headers['Access-Control-Allow-Origin'] = origin
            state.response.headers['Access-Control-Allow-Methods'] = \
                'GET, OPTIONS, PUT, POST'
            state.response.headers['Access-Control-Allow-Headers'] = \
                'origin, authorization, accept, content-type'
            state.response.headers['Access-Control-Allow-Credentials'] = 'true'


class JWTAuthHook(pecan.hooks.PecanHook):
    """A pecan hook that handles authentication with JSON Web Tokens."""

    def on_route(self, state):
        """Check signature in request headers."""
        token = api_utils.decode_token(state.request)
        if token:
            state.request.environ[const.JWT_TOKEN_ENV] = token


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
        hooks=[
            JWTAuthHook(), JSONErrorHook(), CORSHook(),
            pecan.hooks.RequestViewerHook(
                {'items': ['status', 'method', 'controller', 'path', 'body']},
                headers=False, writer=WritableLogger(LOG, logging.DEBUG)
            )
        ]
    )

    beaker_conf = {
        'session.key': 'refstack',
        'session.type': 'ext:database',
        'session.url': CONF.database.connection,
        'session.timeout': 604800,
        'session.validate_key': api_utils.get_token(),
        'session.sa.pool_recycle': 600
    }
    app = SessionMiddleware(app, beaker_conf)

    if CONF.api.app_dev_mode:
        LOG.debug('\n\n <<< Refstack UI is available at %s >>>\n\n',
                  CONF.ui_url)

    return app
