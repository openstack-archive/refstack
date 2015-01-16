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

"""Configuration for running API.

Custom Configurations must be in Python dictionary format:

foo = {'bar':'baz'}

All configurations are accessible at:
pecan.conf
"""

# Server Specific Configurations
server = {
    'port': '8000',
    'host': '0.0.0.0',
    'protocol': 'http'
}

# Pecan Application Configurations
app = {
    'root': 'refstack.api.controllers.root.RootController',
    'modules': ['refstack.api'],
    'static_root': '%(confdir)s/../static',
    'template_path': '%(confdir)s/../templates',
    # The 'debug' option should be false in production servers, but needs to be
    # true in development in order to allow the static_root option to work.
    'debug': False,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}

logging = {
    'loggers': {
        'root': {'level': 'INFO', 'handlers': ['console']},
        'refstack': {'level': 'DEBUG', 'handlers': ['console']}
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        }
    }
}
