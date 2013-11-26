
import flask
from flask.ext.admin.contrib import sqla

from refstack import models

# Global admin object
from .extensions import admin
from .extensions import db


class SecureView(sqla.ModelView):
    def is_accessible(self):
        # let us look at the admin if we're in debug mode
        if flask.current_app.debug:
            return True
        return flask.g.user.su is not False


def init_app(app):
    admin.init_app(app)


def configure_admin():
    admin.add_view(SecureView(models.Cloud, db.session))
    admin.add_view(SecureView(models.User, db.session))
    admin.add_view(SecureView(models.Vendor, db.session))
