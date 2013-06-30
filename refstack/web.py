# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import random
import sqlite3
import sys
from flask import Flask, flash, request, redirect, url_for, render_template, g, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose
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
db = SQLAlchemy(app)


class Vendor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	vendor_name = db.Column(db.String(80), unique=True)
	contact_email = db.Column(db.String(120), unique=True)

	def __repr__(self):
		return '<Vendor %r>' % self.vendor_name


admin = Admin(app)
admin.add_view(ModelView(Vendor, db.session))


@app.route('/', methods=['POST','GET'])
def index():
	vendors = Vendor.query.all()
	return render_template('index.html', vendors = vendors)


if __name__ == '__main__':	
	app.logger.setLevel('DEBUG')
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
