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

    def __init__(self, username, email):
        self.vendor_name = vendor_name
        self.contact_email = contact_email

    def __repr__(self):
        return '<Vendor %r>' % self.vendor_name
        
# 
# @app.before_request
# def before_request():
#     g.db = connect_db()
# 
# @app.teardown_request
# def teardown_request(exception):
#     if hasattr(g, 'db'):
#         g.db.close()
#         
# def query_db(query, args=(), one=False):
#     cur = g.db.execute(query, args)
#     rv = [dict((cur.description[idx][0], value)
#                for idx, value in enumerate(row)) for row in cur.fetchall()]
#     return (rv[0] if rv else None) if one else rv
# 
# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource('schema.sql') as f:
#             db.cursor().executescript(f.read())
#         db.commit()

@app.route('/', methods=['POST','GET'])
def index():
    vendors = Vendor.query.all()
	return render_template('index.html', vendors = vendors)