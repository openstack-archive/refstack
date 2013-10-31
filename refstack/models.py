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
"""striaght up sqlalchemy declarative_base model structure. 

    *I created this because i was having a problem getting 
    the cli to use the models that were generated for the flask 
    webapp. The plan is to use this for both. But I have not 
    started my serious efforts on the web interface.  dl 10.2013

    *For now in dev I have this database in /tmp we can talk 
    about someplace else for it by default. 
"""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker,relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Binary, Boolean

engine = create_engine('sqlite:////tmp/refstack.db', convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))

Base = declarative_base()
Base.query = db.query_property()



class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    vendor = relationship('Vendor',
                             backref=backref('clouds',
                                                lazy='dynamic'))
    name = Column(String(60))
    email = Column(String(200), unique=True)
    email_verified = Column(Boolean)
    openid = Column(String(200), unique=True)
    authorized = Column(Boolean, default=False)
    su = Column(Boolean, default=False)

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid

    def __str__(self):
        return self.name



"""
Note: The vendor list will be pre-populated from the sponsoring company database. 
TODO: better define the vendor object and its relationship with user
it needs the ability to facilitate a login. 
"""
class Vendor(Base):
    __tablename__ = 'vendor'
    id = Column(Integer, primary_key=True)
    vendor_name = Column(String(80), unique=True)
    contact_email = Column(String(120), unique=True)
    contact_name = Column(String(120), unique=False)

    def __str__(self):
        return self.vendor_name



class Cloud(Base):
    """*need to take the time to descibe this stuff in detail. 
    """
    __tablename__ = 'cloud'
    id = Column(Integer, primary_key=True)
    
    label = Column(String(60), unique=False)
    endpoint = Column(String(120), unique=True)
    test_user = Column(String(80), unique=False)
    test_key = Column(String(80), unique=False)
    admin_endpoint = Column(String(120), unique=False)
    admin_user = Column(String(80), unique=False)
    admin_key = Column(String(80), unique=False)



class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    cloud_id = Column(Integer, ForeignKey('cloud.id'))
    cloud = relationship('Cloud',
                          backref=backref('tests',lazy='dynamic'))
    config = Column(String(4096))


    def __init__(self, cloud_id):
        self.cloud_id = cloud_id



class TestStatus(Base):
    __tablename__ = 'test_status'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'))
    test = relationship('Test',
                          backref=backref('status',lazy='dynamic'))
    message = Column(String(1024))
    finished = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.now)


    def __init__(self,test_id, message, finished=False):
        self.test_id = test_id
        self.message = message
        self.finished = finished



class TestResults(Base):
    __tablename__ = 'test_results'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'))
    test = relationship('Test',
                          backref=backref('results',lazy='dynamic'))
    timestamp = Column(DateTime, default=datetime.now)
    blob = Column(Binary)


