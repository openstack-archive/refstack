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
from keystoneclient.v2_0 import client
from refstack.common import *
import refstack.models

class Clouds

class Cloud(object):
    """ Cloud functions"""
    cloud_id = None

    def __init__(self, cloud_id = None):
        """ init method loads specified id or fails"""
        self.cloud_id = cloud_id

        if not cloud_id:
            # we have a new cloud. 
            # do nothing because now we'll call the add method
            return None
        else:
            # load an existing cloud
            self._cloud = models.Cloud.query.filter_by(id=self.cloud_id).first()

            if not self._cloud:
                # cloud not found.. invalid id 
                # maybe I should do someting about this .. 
                return None

            self._keystone = client.Client(username=self._cloud.admin_user,
                                           password=self._cloud.admin_key,
                                           auth_url=self._cloud.admin_endpoint )

            self._end_point = None

    def add(self,endpoint,test_user,test_key,
            admin_endpoint,admin_user,admin_key,vendor_id=None):
        #adds a new cloud to the db
        models.db.session.add(Cloud(endpoint,test_user,test_key,
            admin_endpoint,admin_user,admin_key,vendor_id))
        models.db.session.commit()

    @property
    def end_point(self):
        """end_point property"""
        return self._end_point

    @end_point.setter
    def end_point(self, value):
        self._end_point = value

    def get_config(self):
        """uses end_point and creditials from the specified cloud_id to 
        get a list of services and enpoints from keystone then outputs a
        usable tempest config"""
        
