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

from refstack.tests import api


class TestRefStackApi(api.FunctionalTest):

    def test_root_controller(self):
        actual_response = self.get_json('/')
        expected_response = {'Root': 'OK'}
        self.assertEqual(expected_response, actual_response)

    def test_results_controller(self):
        actual_response = self.get_json('/v1/results/')
        expected_response = {'Results': 'OK'}
        self.assertEqual(expected_response, actual_response)
