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
import os

###############################################################
#
#
#           THIS FILE IS NOT USED
#           (leaveing it around briefly for reference)
#
#
###############################################################

db_path = '/tmp'


class Default(object):
    MAILGUN_KEY = '#@#@#@#@'
    MAILGUN_DOMAIN = 'refstack.org'
    SECRET_KEY = '#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///%s/refstack.db' % (db_path))
    DEBUG = True
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_POST_LOGIN_VIEW = 'dashboard'
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_EMAIL_SENDER = "refstack.org"
    MAIL_SERVER = 'smtp.refstack.org'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'postmaster@refstack.org'
    MAIL_PASSWORD = '1234'
