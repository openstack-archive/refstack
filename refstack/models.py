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

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Test(Base):
    __tablename__ = 'test'

    id = sa.Column(sa.String(36), primary_key=True)
    cpid = sa.Column(sa.String(128), index=True, nullable=False)
    duration_seconds = sa.Column(sa.Integer, nullable=False)
    results = orm.relationship('TestResults', backref='test')
    meta = orm.relationship('TestMeta', backref='test')


class TestResults(Base):
    __tablename__ = 'results'
    __table_args__ = (
        sa.UniqueConstraint('test_id', 'name'),
        sa.UniqueConstraint('test_id', 'uid'),
    )
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    test_id = sa.Column(sa.String(36), sa.ForeignKey('test.id'),
                        index=True, nullable=False, unique=False)
    name = sa.Column(sa.String(1024))
    uid = sa.Column(sa.String(36))


class TestMeta(Base):
    __tablename__ = 'meta'
    __table_args__ = (
        sa.UniqueConstraint('test_id', 'meta_key'),
    )
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    test_id = sa.Column(sa.String(36), sa.ForeignKey('test.id'),
                        index=True, nullable=False, unique=False)
    meta_key = sa.Column(sa.String(64), index=True, nullable=False)
    value = sa.Column(sa.Text())
