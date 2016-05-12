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

"""SQLAlchemy models for Refstack data."""

import uuid

from oslo_config import cfg
from oslo_db.sqlalchemy import models
import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

CONF = cfg.CONF
BASE = declarative_base()


class RefStackBase(models.ModelBase,
                   models.TimestampMixin,
                   models.SoftDeleteMixin):
    """Base class for RefStack Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

    @property
    def metadata_keys(self):  # pragma: no cover
        """Model keys with metadata structure. Will be converted in dict."""
        return dict()

    @property
    def default_allowed_keys(self):  # pragma: no cover
        """Default keys will be present in resulted dict."""
        return ()

    metadata = None


class Test(BASE, RefStackBase):  # pragma: no cover
    """Test."""

    __tablename__ = 'test'

    id = sa.Column(sa.String(36), primary_key=True)
    cpid = sa.Column(sa.String(128), index=True, nullable=False)
    duration_seconds = sa.Column(sa.Integer, nullable=False)
    results = orm.relationship('TestResults', backref='test')
    meta = orm.relationship('TestMeta', backref='test')

    @property
    def _extra_keys(self):
        """Relation should be pointed directly."""
        return ['results', 'meta']

    @property
    def metadata_keys(self):
        """Model keys with metadata structure."""
        return {'meta': {'key': 'meta_key',
                         'value': 'value'}}

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'id', 'created_at', 'duration_seconds', 'meta'


class TestResults(BASE, RefStackBase):  # pragma: no cover
    """Test results."""

    __tablename__ = 'results'
    __table_args__ = (
        sa.UniqueConstraint('test_id', 'name'),
        # TODO(sslypushenko)
        # Constraint should turned on after duplication test uuids issue
        # will be fixed
        # sa.UniqueConstraint('test_id', 'uuid'),
    )
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    test_id = sa.Column(sa.String(36), sa.ForeignKey('test.id'),
                        index=True, nullable=False, unique=False)
    name = sa.Column(sa.String(512, collation='latin1_swedish_ci'),)
    uuid = sa.Column(sa.String(36))

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'name', 'uuid'


class TestMeta(BASE, RefStackBase):  # pragma: no cover
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

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'meta_key', 'value'


class User(BASE, RefStackBase):  # pragma: no cover
    """User information."""

    __tablename__ = 'user'
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    openid = sa.Column(sa.String(128), nullable=False, unique=True,
                       index=True)
    email = sa.Column(sa.String(128))
    fullname = sa.Column(sa.String(128))
    pubkeys = orm.relationship('PubKey', backref='user')

    @property
    def _extra_keys(self):
        """Relation should be pointed directly."""
        return ['pubkeys']

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'openid', 'email', 'fullname', 'pubkeys'


class PubKey(BASE, RefStackBase):  # pragma: no cover
    """User public pubkeys."""

    __tablename__ = 'pubkeys'

    id = sa.Column(sa.String(36), primary_key=True,
                   default=lambda: six.text_type(uuid.uuid4()))
    openid = sa.Column(sa.String(128), sa.ForeignKey('user.openid'),
                       nullable=False, unique=True, index=True)
    format = sa.Column(sa.String(24), nullable=False)
    pubkey = sa.Column(sa.Text(), nullable=False)
    comment = sa.Column(sa.String(128))
    md5_hash = sa.Column(sa.String(32), nullable=False, index=True)

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'id', 'openid', 'format', 'pubkey', 'comment'


class Group(BASE, RefStackBase):  # pragma: no cover
    """Group definition."""

    __tablename__ = 'group'

    id = sa.Column(sa.String(36), primary_key=True,
                   default=lambda: six.text_type(uuid.uuid4()))
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.Text())

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'id', 'name', 'description'


class UserToGroup(BASE, RefStackBase):  # pragma: no cover
    """user-group as many-to-many."""

    __tablename__ = 'user_to_group'

    created_by_user = sa.Column(sa.String(128), nullable=False)
    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_openid = sa.Column(sa.String(128), sa.ForeignKey('user.openid'),
                            nullable=False, index=True)
    group_id = sa.Column(sa.String(36), sa.ForeignKey('group.id'),
                         nullable=False)

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return 'user_openid', 'group_id'


class Organization(BASE, RefStackBase):  # pragma: no cover
    """Organization definition."""

    __tablename__ = 'organization'

    id = sa.Column(sa.String(36), primary_key=True,
                   default=lambda: six.text_type(uuid.uuid4()))
    type = sa.Column(sa.Integer, nullable=False)
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.Text())
    group_id = sa.Column(sa.String(36), sa.ForeignKey('group.id'),
                         nullable=False)
    created_by_user = sa.Column(sa.String(128), sa.ForeignKey('user.openid'),
                                nullable=False)
    properties = sa.Column(sa.Text())

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return ('id', 'type', 'name', 'description', 'group_id',
                'created_by_user', 'properties', 'created_at', 'updated_at')


class Product(BASE, RefStackBase):  # pragma: no cover
    """Product definition."""

    __tablename__ = 'product'

    id = sa.Column(sa.String(36), primary_key=True,
                   default=lambda: six.text_type(uuid.uuid4()))
    product_id = sa.Column(sa.String(36), nullable=True)
    name = sa.Column(sa.String(80), nullable=False)
    description = sa.Column(sa.Text())
    organization_id = sa.Column(sa.String(36),
                                sa.ForeignKey('organization.id'),
                                nullable=False)
    created_by_user = sa.Column(sa.String(128), sa.ForeignKey('user.openid'),
                                nullable=False)
    public = sa.Column(sa.Boolean(), nullable=False)
    properties = sa.Column(sa.Text())
    type = sa.Column(sa.Integer(), nullable=False)
    product_type = sa.Column(sa.Integer(), nullable=False)

    @property
    def default_allowed_keys(self):
        """Default keys."""
        return ('id', 'name', 'description', 'product_id', 'product_type',
                'public', 'properties', 'created_at', 'updated_at',
                'organization_id', 'created_by_user', 'type')
