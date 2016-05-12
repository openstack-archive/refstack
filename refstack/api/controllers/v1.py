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

"""Version 1 of the API."""

from refstack.api.controllers import auth
from refstack.api.controllers import guidelines
from refstack.api.controllers import products
from refstack.api.controllers import results
from refstack.api.controllers import user
from refstack.api.controllers import vendors


class V1Controller(object):
    """Version 1 API controller root."""

    results = results.ResultsController()
    guidelines = guidelines.GuidelinesController()
    auth = auth.AuthController()
    profile = user.ProfileController()
    products = products.ProductsController()
    vendors = vendors.VendorsController()
