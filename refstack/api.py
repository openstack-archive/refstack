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
