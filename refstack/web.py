# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import random
import sqlite3
import sys
from flask import Flask, request, render_template, g, jsonify
from contextlib import closing

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
        
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/', methods=['POST','GET'])
def index():
	return render_template('index.html')