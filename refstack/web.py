# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import random
import sqlite3
import sys
from flask import Flask, request, render_template, g, jsonify


# TODO(JMC): Make me a config var
DATABASE = '/var/www/refstack/database.db'


app = Flask(__name__)
app.debug = True


def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['POST','GET'])
def index():
	return render_template('index.html')