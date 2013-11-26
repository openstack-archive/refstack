#
# Copyright (c) 2013 Piston Cloud Computing, Inc.
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
import os
import logging

import flask
from flask import Flask, abort, flash, request, redirect, url_for, \
    render_template, g, session
from flask_openid import OpenID
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from wtforms import Form, BooleanField, TextField, \
    PasswordField, validators
from flask_mail import Mail

from refstack import app as base_app
from refstack import utils
from refstack.models import *


# TODO(termie): transition all the routes below to blueprints
# TODO(termie): use extensions setup from the create_app() call

app = base_app.create_app()

mail = Mail(app)
# setup flask-openid
oid = OpenID(app)
admin = Admin(app, base_template='admin/master.html')


class SecureView(ModelView):
    def is_accessible(self):
        return g.user.su is not False


admin.add_view(SecureView(Vendor, db))
admin.add_view(SecureView(Cloud, db))
admin.add_view(SecureView(User, db))


@app.before_request
def before_request():
    """Runs before the request itself."""
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()


@app.route('/', methods=['POST', 'GET'])
def index():
    """Index view."""
    if g.user is not None:
        # something else
        clouds = Cloud.query.filter_by(user_id=g.user.id).all()
        return render_template('home.html', clouds=clouds)
    else:
        vendors = Vendor.query.all()
        return render_template('index.html', vendors=vendors)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.

    Has to call into `oid.try_login` to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login("https://login.launchpad.net/",
                          ask_for=['email', 'nickname'])


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
            db.add(User(name, email, session['openid']))
            db.commit()
            return redirect(oid.get_next_url())
    return render_template(
        'create_profile.html', next_url=oid.get_next_url())


@app.route('/delete-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def delete_cloud(cloud_id):
    """Delete function for clouds."""
    c = Cloud.query.filter_by(id=cloud_id).first()

    if not c:
        flash(u'Not a valid Cloud ID!')
    elif not c.user_id == g.user.id:
        flash(u"This isn't your cloud!")
    else:
        db.delete(c)
        db.commit()

    return redirect('/')


@app.route('/edit-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def edit_cloud(cloud_id):
    c = Cloud.query.filter_by(id=cloud_id).first()

    if not c:
        flash(u'Not a valid Cloud ID!')
        return redirect('/')
    elif not c.user_id == g.user.id:
        flash(u"This isn't your cloud!")

    if request.method == 'POST':
        #validate this biotch
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['test_key']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_key']:
            flash(u'Error: All fields are required')
        else:
            c.label = request.form['label']
            c.endpoint = request.form['endpoint']
            c.test_user = request.form['test_user']
            c.test_key = request.form['test_key']
            c.admin_endpoint = request.form['admin_endpoint']
            c.admin_user = request.form['admin_user']
            c.admin_key = request.form['admin_key']

            db.commit()

            flash(u'Cloud Saved!')
            return redirect('/')

    form = dict(label=c.label,
                endpoint=c.endpoint,
                test_user=c.test_user,
                test_key=c.test_key,
                admin_endpoint=c.admin_endpoint,
                admin_user=c.admin_user,
                admin_key=c.admin_key)



    return render_template('edit_cloud.html',form=form)


@app.route('/create-cloud', methods=['GET', 'POST'])
def create_cloud():
    """This is the handler for creating a new cloud."""

    #if g.user is None:
    #    abort(401)
    if request.method == 'POST':
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['test_key']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_key']:
            flash(u'Error: All fields are required')
        else:
            c = Cloud()
            c.user_id = g.user.id
            c.label = request.form['label']
            c.endpoint = request.form['endpoint']
            c.test_user = request.form['test_user']
            c.test_key = request.form['test_key']
            c.admin_endpoint = request.form['admin_endpoint']
            c.admin_user = request.form['admin_user']
            c.admin_key = request.form['admin_key']

            db.add(c)
            db.commit()
            return redirect('/')

    return render_template('create_cloud.html', next_url='/')


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile."""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db.delete(g.user)
            db.commit()
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
            db.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def view_profile():
    """Updates a profile."""
    if g.user is None:
        abort(401)

    return render_template('view_profile.html', user=g.user)


@app.route('/logout')
def logout():
    """Log out."""
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())
