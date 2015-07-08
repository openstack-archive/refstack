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
"""Function list_opts intended for oslo-config-generator.

this tool used for generate config file with help info and default values
for options defined anywhere in application.
All new options must be imported here and must be returned from
list_opts function as list that contain tuple.
Use itertools.chain if config section contain more than one imported module
with options. For example:

...
def list_opts():
    return [
        ('DEFAULT', refstack.db.api.db_opts),
        ('api',
         itertools.chain(refstack.api.first.module.opts,
                         refstack.api.second.modulei.opts,)),
    ]
...
"""
import itertools

import refstack.api.app
import refstack.api.controllers.v1
import refstack.api.controllers.auth
import refstack.db.api


def list_opts():
    """List oslo config options.

    Keep a list in alphabetical order
    """
    return [
        #
        ('DEFAULT', itertools.chain(refstack.api.app.UI_OPTS,
                                    refstack.db.api.db_opts)),
        ('api', itertools.chain(refstack.api.app.API_OPTS,
                                refstack.api.controllers.CTRLS_OPTS)),
        ('osid', refstack.api.controllers.auth.OPENID_OPTS),
    ]
