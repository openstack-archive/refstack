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

from datetime import datetime

from .extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor = db.relationship('Vendor',
                             backref=db.backref('clouds',
                                                lazy='dynamic'))
    name = db.Column(db.String(60))
    email = db.Column(db.String(200), unique=True)
    email_verified = db.Column(db.Boolean)
    openid = db.Column(db.String(200), unique=True)
    authorized = db.Column(db.Boolean, default=False)
    su = db.Column(db.Boolean, default=False)

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid

    def __str__(self):
        return self.name


class ApiKey(db.Model):
    __tablename__ = 'apikey'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    key = db.Column(db.String(200))
    openid = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                           backref=db.backref('apikeys', lazy='dynamic'))


class Vendor(db.Model):
    """Note: The vendor list will be pre-populated from the
    sponsoring company database.
    TODO: better define the vendor object and its relationship with user
    it needs the ability to facilitate a login."""
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(80), unique=True)
    contact_email = db.Column(db.String(120), unique=True)
    contact_name = db.Column(db.String(120), unique=False)

    def __str__(self):
        return self.vendor_name


class Cloud(db.Model):
    """*need to take the time to descibe this stuff in detail.
    """
    __tablename__ = 'cloud'
    id = db.Column(db.Integer, primary_key=True)

    label = db.Column(db.String(60), unique=False)
    endpoint = db.Column(db.String(120), unique=True)
    test_user = db.Column(db.String(80), unique=False)
    test_key = db.Column(db.String(80), unique=False)
    admin_endpoint = db.Column(db.String(120), unique=False)
    admin_user = db.Column(db.String(80), unique=False)
    admin_key = db.Column(db.String(80), unique=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                           backref=db.backref('clouds', lazy='dynamic'))


class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    cloud_id = db.Column(db.Integer, db.ForeignKey('cloud.id'))
    cloud = db.relationship('Cloud',
                            backref=db.backref('tests', lazy='dynamic'))
    config = db.Column(db.String(4096))

    def __init__(self, cloud_id):
        self.cloud_id = cloud_id


class TestStatus(db.Model):
    __tablename__ = 'test_status'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    test = db.relationship('Test',
                           backref=db.backref('status', lazy='dynamic'))
    message = db.Column(db.String(1024))
    finished = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, test_id, message, finished=False):
        self.test_id = test_id
        self.message = message
        self.finished = finished


class TestResults(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    test = db.relationship('Test',
                           backref=db.backref('results', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    subunit = db.Column(db.String(8192))
    blob = db.Column(db.Binary)
