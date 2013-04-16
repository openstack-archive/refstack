# LICENSE HERE
"""
Simple Refstack website.
"""

import os
import sys
import random
from flask import Flask, request, render_template, g, jsonify
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site


PORT = 80

app = Flask(__name__)
app.debug = True


@app.route('/', methods=['POST','GET'])
def index():
	return render_template('index.html')


resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)
app.listeningPort = reactor.listenTCP(PORT, site)

reactor.run()