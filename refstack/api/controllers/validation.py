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

"""Base for controllers with validation."""

import json

import pecan
from pecan import rest


class BaseRestControllerWithValidation(rest.RestController):
    """Rest controller with validation.

    Controller provides validation for POSTed data
    exposed endpoints:
    POST base_url/
    GET base_url/<item uid>
    GET base_url/schema
    """

    __validator__ = None

    _custom_actions = {
        "schema": ["GET"],
    }

    def __init__(self):  # pragma: no cover
        """Init."""
        if self.__validator__:
            self.validator = self.__validator__()
        else:
            raise ValueError("__validator__ is not defined")

    def store_item(self, item_in_json):  # pragma: no cover
        """Handler for storing item. Should return new item id."""
        raise NotImplementedError

    @pecan.expose('json')
    def schema(self):
        """Return validation schema."""
        return self.validator.schema

    @pecan.expose('json')
    def post(self, ):
        """POST handler."""
        self.validator.validate(pecan.request)
        item = json.loads(pecan.request.body)
        item_id = self.store_item(item)
        pecan.response.status = 201
        return item_id
