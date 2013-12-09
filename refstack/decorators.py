#-*- coding: utf-8 -*-

# This file based on MIT licensed code at: https://github.com/imwilsonxu/fbone

from functools import wraps

from flask import abort
from flask.ext.login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
