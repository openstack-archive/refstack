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
"""
SQLAlchemy models for Refstack data.
"""

import datetime

from oslo.config import cfg
from oslo.db.sqlalchemy import models
from oslo.utils import timeutils
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

CONF = cfg.CONF
BASE = declarative_base()


class RefStackBase(models.ModelBase, models.TimestampMixin):

    """Base class for RefStack Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}
    created_at = sa.Column(sa.DateTime(), default=datetime.datetime.utcnow,
                           nullable=False)
    updated_at = sa.Column(sa.DateTime())
    deleted_at = sa.Column(sa.DateTime)
    deleted = sa.Column(sa.Integer, default=0)
    metadata = None

    def delete(self, session=None):
        """Delete this object."""
        self.deleted = self.id
        self.deleted_at = timeutils.utcnow()
        self.save(session=session)


class Test(BASE, RefStackBase):

    """Test."""

    __tablename__ = 'test'

    id = sa.Column(sa.String(36), primary_key=True)
    cpid = sa.Column(sa.String(128), index=True, nullable=False)
    duration_seconds = sa.Column(sa.Integer, nullable=False)
    results = orm.relationship('TestResults', backref='test')
    meta = orm.relationship('TestMeta', backref='test')


class TestResults(BASE, RefStackBase):

    """Test results."""

    __tablename__ = 'results'
    __table_args__ = (
        sa.UniqueConstraint('test_id', 'name'),
        sa.UniqueConstraint('test_id', 'uid'),
    )
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    test_id = sa.Column(sa.String(36), sa.ForeignKey('test.id'),
                        index=True, nullable=False, unique=False)
    name = sa.Column(sa.String(512))
    uid = sa.Column(sa.String(36))


class TestMeta(BASE, RefStackBase):

    """Test metadata."""

    __tablename__ = 'meta'
    __table_args__ = (
        sa.UniqueConstraint('test_id', 'meta_key'),
    )
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    test_id = sa.Column(sa.String(36), sa.ForeignKey('test.id'),
                        index=True, nullable=False, unique=False)
    meta_key = sa.Column(sa.String(64), index=True, nullable=False)
    value = sa.Column(sa.Text())
