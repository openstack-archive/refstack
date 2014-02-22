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
#
"""Simple script for importing the vendor
list csv file provided by the foundation"""
from refstack.models import db, Vendor
import csv

_file = 'members_sponsors_20131030.csv'

with open(_file, 'rb') as csvfile:
    parsed = csv.reader(csvfile, delimiter=',')
    for row in parsed:
        try:
            vendor = Vendor()
            vendor.vendor_name = row[1]
            vendor.contact_email = row[3]
            db.add(vendor)
            db.commit()
        except:
            print 'vendor skipped:'+row[1]
