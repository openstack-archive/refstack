# Copyright (c) 2015 Mirantis, Inc.
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
"""Constants for Refstack API."""

# Names of input parameters for request
START_DATE = 'start_date'
END_DATE = 'end_date'
CPID = 'cpid'
PAGE = 'page'
SIGNED = 'signed'
VERIFICATION_STATUS = 'verification_status'
PRODUCT_ID = 'product_id'
ALL_PRODUCT_TESTS = 'all_product_tests'
OPENID = 'openid'
USER_PUBKEYS = 'pubkeys'

# Guidelines tests requests parameters
ALIAS = 'alias'
FLAG = 'flag'
TYPE = 'type'
TARGET = 'target'

# OpenID parameters
OPENID_MODE = 'openid.mode'
OPENID_NS = 'openid.ns'
OPENID_RETURN_TO = 'openid.return_to'
OPENID_CLAIMED_ID = 'openid.claimed_id'
OPENID_IDENTITY = 'openid.identity'
OPENID_REALM = 'openid.realm'
OPENID_NS_SREG = 'openid.ns.sreg'
OPENID_NS_SREG_REQUIRED = 'openid.sreg.required'
OPENID_NS_SREG_EMAIL = 'openid.sreg.email'
OPENID_NS_SREG_FULLNAME = 'openid.sreg.fullname'
OPENID_ERROR = 'openid.error'

# User session parameters
CSRF_TOKEN = 'csrf_token'
USER_OPENID = 'user_openid'

# Test metadata fields
USER = 'user'
SHARED_TEST_RUN = 'shared'

# Test verification statuses
TEST_NOT_VERIFIED = 0
TEST_VERIFIED = 1

# Roles
ROLE_USER = 'user'
ROLE_OWNER = 'owner'
ROLE_FOUNDATION = 'foundation'

# Organization types.
# OpenStack Foundation
FOUNDATION = 0
# User's private unofficial Vendor (allows creation and testing
# of user's products)
PRIVATE_VENDOR = 1
# Vendor applied and waiting for official status.
PENDING_VENDOR = 2
# Official Vendor approved by the Foundation.
OFFICIAL_VENDOR = 3

# Product object types.
CLOUD = 0
SOFTWARE = 1

# Product specific types.
DISTRO = 0
PUBLIC_CLOUD = 1
HOSTED_PRIVATE_CLOUD = 2

JWT_TOKEN_HEADER = 'Authorization'
JWT_TOKEN_ENV = 'jwt.token'
JWT_VALIDATION_LEEWAY = 42
