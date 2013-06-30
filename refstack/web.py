# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import random
import sqlite3
import sys
from flask import Flask, request, render_template, g, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing


app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/refstack/database.db'
db = SQLAlchemy(app)

class Vendor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	vendor_name = db.Column(db.String(80), unique=True)
	contact_email = db.Column(db.String(120), unique=True)

	def __init__(self, vendor_name, contact_email):
		self.vendor_name = vendor_name
		self.contact_email = contact_email

	def __repr__(self):
		return '<Vendor %r>' % self.vendor_name

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

	def __init__(self, endpoint, test_user, test_key):
		self.endpoint = endpoint
		self.test_user = test_user
		self.test_key = test_key

	def __repr__(self):
		return '<Cloud %r>' % self.endpoint


@app.route('/', methods=['POST','GET'])
def index():
	vendors = Vendor.query.all()
	return render_template('index.html', vendors = vendors)