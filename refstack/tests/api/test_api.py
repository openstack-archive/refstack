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
import json
import uuid

from refstack.tests import api


class TestRefStackApi(api.FunctionalTest):

    def test_root_controller(self):
        """Test request to root."""
        actual_response = self.get_json('/')
        expected_response = {'Root': 'OK'}
        self.assertEqual(expected_response, actual_response)

    def test_results_controller(self):
        """Test results endpoint."""
        results = json.dumps({
            'cpid': 'foo',
            'duration_seconds': 10,
            'results': [
                {'name': 'tempest.foo.bar'},
                {'name': 'tempest.buzz',
                 'uid': '42'}
            ]
        })
        actual_response = self.post_json('/v1/results/', params=results)
        self.assertIn('test_id', actual_response)
        try:
            uuid.UUID(actual_response.get('test_id'), version=4)
        except ValueError:
            self.fail("actual_response doesn't contain test_is")
