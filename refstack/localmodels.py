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
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker,relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

engine = create_engine('sqlite:////tmp/refstack.db', convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))

Base = declarative_base()
Base.query = db.query_property()


class Cloud(Base):
    __tablename__ = 'cloud'
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(120), unique=True)
    test_user = Column(String(80), unique=False)
    test_key = Column(String(80), unique=False)
    admin_endpoint = Column(String(120), unique=False)
    admin_user = Column(String(80), unique=False)
    admin_key = Column(String(80), unique=False)

    def __init__(self,
                 endpoint,
                 test_user,
                 test_key,
                 admin_endpoint,
                 admin_user,
                 admin_key):
        self.endpoint = endpoint
        self.test_user = test_user
        self.test_key = test_key
        self.admin_endpoint = admin_endpoint
        self.admin_user = admin_user
        self.admin_key = admin_key
    