#
# Copyright (c) 2014 Piston Cloud Computing, Inc. All Rights Reserved.
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
#
from refstack import app as base_app
import unittest


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.app = base_app.create_app().test_client()

    def test_nothing(self):
        # make sure the shuffled sequence does not lose any elements
        pass

if __name__ == '__main__':
    unittest.main()
