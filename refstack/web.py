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

import flask
from flask import abort, flash, request, redirect, url_for, \
    render_template, g, session, make_response, send_file
from flask_mail import Mail
from refstack import app as base_app
from refstack.extensions import db
from refstack.extensions import oid
from refstack.models import Cloud
from refstack.models import Test
from refstack.models import User
from refstack.models import Vendor
from refstack.tools.tempest_tester import TempestTester

app = base_app.create_app()
mail = Mail(app)
public_routes = ['/post-result', '/get-miniconf']


@app.before_request
def before_request():
    """Runs before the request itself."""
    if request.path not in public_routes:
        g.user = None
        if 'openid' in session:
            flask.g.user = User.query.\
                filter_by(openid=session['openid']).first()


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
    return oid.try_login(
        "https://login.launchpad.net/",
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
            db.session.add(User(name, email, session['openid']))
            db.session.commit()
            return redirect(oid.get_next_url())
    return render_template(
        'create_profile.html', next_url=oid.get_next_url())


@app.route('/delete-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def delete_cloud(cloud_id):
    """Delete function for clouds."""
    cloud = Cloud.query.filter_by(id=cloud_id).first()

    if not cloud:
        flash(u'Not a valid Cloud ID!')
    elif not cloud.user_id == g.user.id:
        flash(u"This isn't your cloud!")
    else:
        # Delete all the tests associated with the cloud from DB
        for test in cloud.tests:
            db.session.delete(test)
        # Delete the cloud from DB
        db.session.delete(cloud)
        db.session.commit()

    return redirect('/')


@app.route('/delete-test/<int:test_id>', methods=['GET', 'POST'])
def delete_test(test_id):
    """Delete function for tests."""
    test = Test.query.filter_by(id=test_id).first()

    if not test:
        flash(u'Not a valid Test ID!')
    elif not test.cloud.user_id == g.user.id:
        flash(u"This isn't your test!")
    else:
        db.session.delete(test)
        db.session.commit()

    return redirect('/')


@app.route('/edit-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def edit_cloud(cloud_id):
    cloud = Cloud.query.filter_by(id=cloud_id).first()

    if not cloud:
        flash(u'Not a valid Cloud ID!')
        return redirect('/')
    elif not cloud.user_id == g.user.id:
        flash(u"This isn't your cloud!")

    if request.method == 'POST':
        # some validation
        # todo: do this smarter
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        else:
            cloud.label = request.form['label']
            cloud.endpoint = request.form['endpoint']
            cloud.test_user = request.form['test_user']
            cloud.admin_endpoint = request.form['admin_endpoint']
            cloud.endpoint_v3 = request.form['endpoint_v3']
            cloud.version = request.form['version']
            cloud.admin_user = request.form['admin_user']

            db.session.commit()

            flash(u'Cloud Saved!')
            return redirect('/')

    form = dict(label=cloud.label,
                endpoint=cloud.endpoint,
                endpoint_v3=cloud.endpoint_v3,
                admin_endpoint=cloud.admin_endpoint,
                admin_user=cloud.admin_user,
                version=cloud.version,
                test_user=cloud.test_user)

    return render_template('edit_cloud.html', form=form)


@app.route('/create-cloud', methods=['GET', 'POST'])
def create_cloud():
    """This is the handler for creating a new cloud."""

    if g.user is None:
        abort(401)
    if request.method == 'POST':
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        else:
            new_cloud = Cloud()
            new_cloud.user_id = g.user.id
            new_cloud.label = request.form['label']
            new_cloud.endpoint = request.form['endpoint']
            new_cloud.test_user = request.form['test_user']
            new_cloud.admin_endpoint = request.form['admin_endpoint']
            new_cloud.endpoint_v3 = request.form['endpoint_v3']
            new_cloud.version = request.form['version']
            new_cloud.admin_user = request.form['admin_user']

            db.session.add(new_cloud)
            db.session.commit()
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


@app.route('/test-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def test_cloud(cloud_id):
    """Handler for creating a new test."""

    cloud = Cloud.query.filter_by(id=cloud_id).first()

    if not cloud:
        flash(u'Not a valid Cloud ID!')
        return redirect('/')
    elif not cloud.user_id == g.user.id:
        flash(u"This isn't your cloud!")
        return redirect('/')

    if request.method == 'POST':

        # Check for required fields
        REQUIRED_FIELDS = ('pw_admin', 'pw_user')
        if not all(request.form[field] for field in REQUIRED_FIELDS):
            flash(u'Error: All fields are required')
        else:
            # Create new test object in db
            new_test = Test()
            new_test.cloud = cloud
            new_test.cloud_id = cloud.id
            db.session.add(new_test)
            db.session.commit()

            # Construct confJSON with the passwords provided
            # and using the same user for alt_user
            pw_admin = request.form['pw_admin']
            pw_user = request.form['pw_user']
            pw_alt = request.form['pw_user']
            json_str = '{"identity":{"password":"%s","admin_password":"%s",\
"alt_password":"%s"}}' % (pw_user, pw_admin, pw_alt)

            # Excute the test
            try:
                TempestTester(new_test.id).execute_test(json_str)
                flash(u'Test started!')
            except ValueError:
                flash(u'Fail to start test!')

            return redirect('/')

    names = dict(user=cloud.test_user, admin=cloud.admin_user)

    return render_template('test_cloud.html', next_url='/', names=names)


@app.route('/get-script', methods=['GET'])
def get_script():
    """Return a generic python script to be run a remote test runner."""

    return send_file('tools/execute_test.py', mimetype='text/plain')


@app.route('/get-miniconf', methods=['GET'])
def get_miniconf():
    """Return a JSON of mini tempest conf to a remote test runner."""

    test_id = request.args.get('test_id', '')
    try:
        response = make_response(TempestTester(test_id).generate_miniconf())
        response.headers["Content-Disposition"] = \
            "attachment; filename=miniconf.json"
        return response
    except ValueError:
        return make_response('Invalid test ID')


@app.route('/get-testcases', methods=['GET'])
def get_testcases():
    """Return a JSON of tempest test cases to a remote test runner."""

    test_id = request.args.get('test_id', '')
    try:
        response = make_response(TempestTester(test_id).generate_testcases())
        response.headers["Content-Disposition"] = \
            "attachment; filename=testcases.json"
        return response
    except ValueError:
        return make_response('Invalid test ID')


@app.route('/post-result', methods=['POST'])
def post_result():
    """Receive tempest test result from a remote test runner."""
    # todo: come up with some form of authentication
    # Im sure we can come with something more elegant than this
    # but it should work for now.
    #print request.files
    f = request.files['file']
    if f:
        if request.args.get('test_id', ''):
            # this data is for a specific test triggered by the gui and we
            # want to relate it
            new_test = Test.query.\
                filter_by(id=request.args.get('test_id', '')).first()
            new_test.subunit = f.read()
            new_test.finished = True

        else:
            # anonymous data .. we still want to capture it
            new_test = Test()
            new_test.subunit = f.read()
            new_test.finished = True
            db.session.add(new_test)

        db.session.commit()

    # todo .. set up error handling with correct response codes
    return make_response('')


@app.route('/show-status/<int:test_id>', methods=['GET', 'POST'])
def show_status(test_id):
    """Handler for showing test status."""

    test = Test.query.filter_by(id=test_id).first()

    if not test:
        flash(u'Not a valid Test ID!')
        return redirect('/')
    elif not test.cloud.user_id == g.user.id:
        flash(u"This isn't your test!")
        return redirect('/')

    # This is a place holder for now
    ''' TODO: Generate the appropriate status page '''

    return render_template('show_status.html', next_url='/', test=test)


@app.route('/show-report/<int:test_id>', methods=['GET', 'POST'])
def show_report(test_id):
    """Handler for showing test report."""

    test = Test.query.filter_by(id=test_id).first()

    if not test:
        flash(u'Not a valid Test ID!')
        return redirect('/')
    elif not test.cloud.user_id == g.user.id:
        flash(u"This isn't your test!")
        return redirect('/')

    # This is a place holder for now
    ''' TODO: Generate the appropriate report page '''
    ''' ForNow: send back the subunit data stream for debugging '''

    response = make_response(test.subunit)
    response.headers["Content-Disposition"] = \
        "attachment; filename=subunit.txt"
    response.content_type = "text/plain"
    return response

    # return render_template('show_report.html', next_url='/', test=test)
