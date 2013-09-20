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
from refstack.common import *


class Cloud:
    """ Vendor functions"""
    id = None

    def __init__(self, id):
        """ init method loads specified id or fails"""
        self.id = id

    @def end_point():
        doc = "The end_point property."
        def fget(self):
            return self._end_point
        def fset(self, value):
            self._end_point = value
        def fdel(self):
            del self._end_point
        return locals()

    foo = property(**foo())

    def tests(self, cloud_
        id = None):
        """ returns object populated with test objects that belong to 
        this user and filter
        ed by cloud_id if specified """
        
