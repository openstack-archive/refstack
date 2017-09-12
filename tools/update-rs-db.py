#!/usr/bin/env python

# Copyright (c) 2017 OpenStack Foundation
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

"""
Test result update & verify script for the local refstack database.
"""

import argparse
import datetime
import json
import jwt
import os
import requests
import sys

from collections import namedtuple


def generate_token(keyfile, _id):
    # get private key in string format
    with open(keyfile) as pemfile:
        secret = pemfile.read().rstrip()
    exp = datetime.timedelta(seconds=100500)
    payload =\
        {
            "user_openid": _id,
            "exp": datetime.datetime.now() + exp
        }
    token = jwt.encode(payload, secret, algorithm="RS256")
    with open("./token", "w+") as tokenfile:
        tokenfile.write(str(token))
        print("token stored in the current working directory.")


def testAuth(link, tokenfile):
    auth_test_url = link.split("/v1")[0] + "/#/profile"
    with open(tokenfile) as tokenfile:
        token = tokenfile.read().strip()
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(auth_test_url, headers)
    if response.status_code == 200:
        return True, token
    else:
        print("token auth failed. status code = %d" % (response.status_code))
        print("auth failure detail: %s" % (response.text))
        return False, None


def getData(entry):
    guidelines = ["2015.03", "2015.04", "2015.05", "2015.07", "2016.01",
                  "2016.08", "2017.01", "2017.09"]
    # NOTE: Storage is an alias of Object
    components = ["platform", "compute", "storage", "object"]
    if len(entry) < 10:
        return None, None, None
    refstackLink = entry[9].strip()
    guideline = entry[4].strip()
    target = entry[5].lower().strip()
    if refstackLink:
        testId = refstackLink.split("/")[-1]
    else:
        refstackLink = None
        testId = None
    if guideline not in guidelines:
        guideline = None
    if target not in components:
        target = None
    elif target == "storage":
        target = "object"
    return testId, guideline, target


def linkChk(link, token):
    """Check existence of and access to api result link"""
    print("checking result with a test ID of: %s" % (link.split("/")[-1]))
    if not link:
        return False
    try:
        if " " in link:
            return False
        headers = {"Authorization": "Bearer " + token}
        response = requests.get(link, headers)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 401 or response.status_code == 403:
            print("Authentication Failed. link check response code: %d" %
                  (response.status_code))
            return False
        elif response.status_code == 400:
            print("Malformed Request. link response code: %d" %
                  (response.status_code))
            return False
        else:
            print("Link check response_status_code = %d" %
                  (response.status_code))
            print("Link check response detail: %s" % (response.text))
            return False
    except requests.exceptions as err:
        print(err)
        return False


def updateField(header, apiLink, raw_data):
    """Update a given metadata field"""
    valid_keytype = ["shared", "guideline", "target"]
    keytype = raw_data.type
    keyval = raw_data.value
    if keytype not in valid_keytype or not keyval:
        updresult = "%s keypair does not exist" % (keytype)
        return updresult, False
    link = apiLink.strip() + "/meta/" + keytype
    response = requests.post(link, data=keyval, headers=header)
    if response.status_code != 201:
        print("update response status code=%d" %
              (response.status_code))
        print("update response text=%s" % (response.text))
        updresult = ("%s field update failed. reason: %s" %
                     (keytype, response.text.replace(",", "  ")))
        return updresult, False
    else:
        updresult = ("%s field update successful," % (keytype))
        return updresult, True


def updateResult(apiLink, target, guideline, token, record):
    """Update metadata for result and verify if all updates are a success"""
    MetadataField = namedtuple("MetadataField", ["type", "value"])
    success = []
    header = {"Authorization": "Bearer " + token}
    with open(record, "a") as r:
        r.write(str(datetime.datetime.now()) + "," + apiLink + ",")
        # update the shared field
        data = MetadataField("shared", "true")
        shared_result, shared_status = updateField(header, apiLink, data)
        r.write(shared_result)
        success.append(shared_status)
        # update the target field
        data = MetadataField("target", target)
        target_result, target_status = updateField(header, apiLink, data)
        r.write(target_result)
        success.append(target_status)
        # update the guideline field
        data = MetadataField("guideline", guideline + ".json")
        gl_result, gl_status = updateField(header, apiLink, data)
        r.write(gl_result)
        success.append(gl_status)
        if not all(success):
            r.write("unable to verify.\n")
            return False
        # if there were no update failures, we can verify the result
        # this is the operation most likely to fail, so extra checks are
        # in order
        print("Test Result updated successfully. Attempting verification.")
        try:
            response = requests.put(apiLink,
                                    json={"verification_status": 1},
                                    headers=header)
        except Exception as ex:
            print("Exception raised while verifying test result: %s" %
                  (str(ex)))
            r.write("verification failed: %s\n" % (str(ex)))
            return False
        updated = verification_chk(apiLink, header)
        if response.status_code not in (200, 201):
            print("verification failure status code=%d" %
                  (response.status_code))
            print("verification failure detail=%s" %
                  (response.text))
            r.write("verification unsuccessful: detail: %s\n" %
                    (response.text))
            return False
        elif not updated:
            print("verification_status field failed to update")
            r.write("verification status update failed. detail: %s\n" %
                    (response.text))
            return False
        else:
            print("Test result verified!\n")
            r.write("Test result successfully verified\n")
            return True


def verification_chk(link, header):
    try:
        response = requests.get(link, header)
        status = int(response.json()["verification_status"])
        if status == 1:
            return True
        else:
            return False
    except Exception as ex:
        print(
            "Exception raised while ensuring verification status update: %s" %
            str(ex))
        return False


def main():
    linect = 0
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    # token handling options- we either need the path of a working token,
    # or the data to generate a new token
    token_flags = parser.add_mutually_exclusive_group(required=True)
    token_flags.add_argument("--tokenfile", type=str, action="store",
                             help=("Absolute path to a json web token to "
                                   "use to auth to the RefStack API"))
    token_flags.add_argument("--generate", nargs=2,
                             metavar=("ssh-key", "openstack-id"),
                             help=("data needed to create a new auth token "
                                   "ssh - key should be an absolute path to "
                                   "a rsa ssh key. openstack - id indicates "
                                   "an openstackid url to use for auth. "
                                   "example: "
                                   "https://openstackid.org/<your id >"))
    # non token-related flags
    parser.add_argument("--file", "-f", metavar="f", type=str, action="store",
                        required=True,
                        help="csv source for the data to use in updates")
    parser.add_argument(
        "--endpoint", "-e", metavar="e",
        type=str, action="store", required=True,
        help="the base URL of the endpoint. ex: http://examplerefstack.com/v1")
    parser.add_argument("--record", "-r", metavar="r", type=str,
                        action="store", default="verification_results.csv",
                        help=("name of file to output update & verification "
                              "run record data into"))
    args = parser.parse_args()
    infile = args.file
    record = args.record
    endpoint = args.endpoint
    if args.generate:
        keypath = args.generate[0]
        _id = args.generate[1]
        generate_token(keypath, _id)
        tokenfile = "./token"
    else:
        tokenfile = args.tokenfile
    auth_success, token = testAuth(endpoint, tokenfile)
    if not auth_success:
        print(("Please enter either a valid token or an openstackid and the "
              "absolute path to an rsa ssh key."))
        sys.exit(1)
    with open(infile) as f:
        for line in f:
            linect = linect + 1
            entry = line.split(",")
            testId, guideline, target = getData(entry)
            if None in (testId, guideline, target):
                print(("entry found at line %d cannot be updated and "
                       "verified: entry incomplete.\n") % (linect))
            else:
                apiLink = os.path.join(endpoint, "results", testId)
                testResult = linkChk(apiLink, token)
                if testResult:
                    if testResult.get("verification_status"):
                        print("Result has been verified.\n")
                    else:
                        print(
                            "Result link is valid. Updating result with ID %s"
                            % (testId))
                        success = updateResult(apiLink, target, guideline,
                                               token, record)
                        if not success:
                            print(("update of the results with the ID %s "
                                   "failed. please recheck your spreadsheet "
                                   "and try again" % (testId)))
                else:
                    print(("the test result: % s cannot be updated or "
                          "verified due to a broken result link." % (testId)))


main()
