#!/usr/bin/env python
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
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app import app

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
                             backref=db.backref('clouds',
                                                lazy='dynamic'))
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
