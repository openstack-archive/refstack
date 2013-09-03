# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import random
import sqlite3
import sys
from flask import Flask, abort, flash, request, redirect, url_for, render_template, g, session
from flask_openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from sqlalchemy.exc import IntegrityError
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from flask_mail import Mail
import requests    

app = Flask(__name__)

app.config['MAILGUN_KEY'] = 'key-7o9l9dupikfpsdvqi0ewot-se8g1hz64'
app.config['MAILGUN_DOMAIN'] = 'hastwoparents.com'


app.config['SECRET_KEY'] = 'GIANT_UGLY-SECRET-GOES-H3r3'
db_path = os.path.abspath(os.path.join(os.path.basename(__file__), "../"))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///%s/refstack.db' % (db_path))
app.config['DEBUG'] = True

app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = app.config['SECRET_KEY']
app.config['SECURITY_POST_LOGIN_VIEW'] = 'dashboard'
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_EMAIL_SENDER'] = "admin@hastwoparents.com"

app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'postmaster@hastwoparents.com'
app.config['MAIL_PASSWORD'] = '0sx00qlvqbo3'

mail = Mail(app)

# setup flask-openid
oid = OpenID(app)
db = SQLAlchemy(app)


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(80), unique=True)
    contact_email = db.Column(db.String(120), unique=True)
    
    def __str__(self):
        return self.vendor_name

class Cloud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor = db.relationship('Vendor',
        backref=db.backref('clouds', lazy='dynamic'))

    endpoint = db.Column(db.String(120), unique=True)
    test_user = db.Column(db.String(80), unique=True)
    test_key = db.Column(db.String(80), unique=True)
    admin_endpoint = db.Column(db.String(120), unique=True)
    admin_user = db.Column(db.String(80), unique=True)
    admin_key = db.Column(db.String(80), unique=True)
    
    def __str__(self):
        return self.endpoint

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(200))
    openid = db.Column(db.String(200), unique=True)

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid
    
    def __str__(self):
        return self.name

# IndexView = AdminIndexView(url="/")
admin = Admin(app) #, index_view=IndexView)

class SecureView(ModelView):
    def is_accessible(self):
        return g.user is not None

admin.add_view(SecureView(Vendor, db.session))
admin.add_view(SecureView(Cloud, db.session))
admin.add_view(SecureView(User, db.session))


@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()


@app.route('/', methods=['POST','GET'])
def index():
    vendors = Vendor.query.all()
    return render_template('index.html', vendors = vendors)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login("https://login.launchpad.net/", ask_for=['email', 'nickname'])
    # return render_template('login.html', next=oid.get_next_url(),
    #                       error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            db.session.add(User(name, email, session['openid']))
            db.session.commit()
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())


@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(g.user)
            db.session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            db.session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())



if __name__ == '__main__':  
    app.logger.setLevel('DEBUG')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
