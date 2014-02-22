#
# Copyright (c) 2013 Piston Cloud Computing, Inc. All Rights Reserved.
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
"""Basic API code.

This is using Flask-Restless at the moment because it is super simple,
but probably should be moved to a more versatile framework like
Flask-Restful later on.
"""

import flask
from flask.ext import restless

from refstack import models
from refstack.extensions import api


def init_app(app, *args, **kw):
    api.init_app(app, *args, **kw)


def access_control(**kw):
    if not flask.g.user:
        raise _not_authorized()

    if not flask.g.user.su:
        return _not_authorized()

    # That's it, we're defaulting to superuser only access
    # until we flesh this out further


ALL_METHODS = {'GET_SINGLE': [access_control],
               'GET_MANY': [access_control],
               'PUT_SINGLE': [access_control],
               'PUT_MANY': [access_control],
               'POST': [access_control],
               'DELETE': [access_control]}


def configure_api(app):
    cloud_api = api.create_api_blueprint(models.Cloud,
                                         preprocessors=ALL_METHODS)
    cloud_api.before_request(authenticate)
    app.register_blueprint(cloud_api)


def _not_authorized():
    return restless.ProcessingException(message='Not Authorized',
                                        status_code=401)


def authenticate():
    # If we're already authenticated, we can ignore this
    if flask.g.user:
        return

    # Otherwise check headers
    openid = flask.request.headers.get('X-AUTH-OPENID')
    if openid:
        # In debug mode accept anything
        if flask.current_app.debug and False:
            flask.g.user = models.User.query.filter_by(openid=openid).first()
            return

        apikey = flask.request.headers.get('X-AUTH-APIKEY')
        apikey_ref = models.ApiKey.query.filter_by(key=apikey)
        if apikey_ref['openid'] == openid:
            flask.g.user = apikey_ref.user
