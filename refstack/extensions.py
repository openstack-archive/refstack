# -*- coding: utf-8 -*-

# This file based on MIT licensed code at: https://github.com/imwilsonxu/fbone

from flask.ext.admin import Admin
admin = Admin()

from flask.ext.restless import APIManager
api = APIManager()

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

# TODO(termie): not used yet
#from flask.ext.cache import Cache
#cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.openid import OpenID
oid = OpenID()
