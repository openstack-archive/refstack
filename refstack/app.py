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
import os
from flask import Flask, render_template
from .config import DefaultConfig
from refstack import admin
from refstack import api
from .extensions import db
from .extensions import oid


from refstack import utils


INSTANCE_FOLDER_PATH = utils.INSTANCE_FOLDER_PATH


# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = tuple()
#    frontend,
#    user,
#    settings,
#    api,
#    admin,
#)


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    # NOTE(termie): Flask has this new instance_path stuff that allows
    # you to keep config and such in different places, but I don't really
    # see how that is going to be very helpful, so we're going to stick
    # to using config relative to the root unless we explicitly set such
    # a path in the INSTANCE_FOLDER_PATH environment variable.
    app = Flask(app_name,
                instance_path=INSTANCE_FOLDER_PATH,
                instance_relative_config=True)

    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)

    if app.debug:
        print utils.dump_config(app)

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # If we've set the INSTANCE_FOLDER_PATH environment var, this may be
    # loaded from an instance folder, otherwise relative to flask.root_path.
    #   http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('refstack.cfg', silent=True)

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)

    # flask-admin
    admin.init_app(app)
    admin.configure_admin(app)

    # flask-restless
    api.init_app(app, flask_sqlalchemy_db=db)
    api.configure_api(app)

    ## flask-mail
    #mail.init_app(app)

    ## flask-cache
    #cache.init_app(app)

    ## flask-babel
    #babel = Babel(app)

    #@babel.localeselector
    #def get_locale():
    #    accept_languages = app.config.get('ACCEPT_LANGUAGES')
    #    return request.accept_languages.best_match(accept_languages)

    ## flask-login
    #login_manager.login_view = 'frontend.login'
    #login_manager.refresh_view = 'frontend.reauth'

    #@login_manager.user_loader
    #def load_user(id):
    #    return User.query.get(id)
    #login_manager.setup_app(app)

    # flask-openid
    oid.init_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):

    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handlers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(
        info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    #app.logger.info("testing info.")
    #app.logger.warn("testing warn.")
    #app.logger.error("testing error.")

    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_USERNAME'],
                               app.config['ADMINS'],
                               'O_ops... %s failed!' % app.config['PROJECT'],
                               (app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(mail_handler)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500
