#!/usr/bin/python

import argparse
import datetime
import requests
import os
import json


def getData(entry):
    guidelines = ["2015.03", "2015.04", "2015.05", "2015.07", "2016.01",
                  "2016.08", "2017.01"]
    components = ["Platform", "Compute", "Storage"]
    if len(entry) < 10:
        return None, None, None
    if entry[9] != "" and entry[9] != " ":
        refstackLink = entry[9]
        testId = refstackLink.split("/")[-1]
    else:
        refstackLink = None
        testId = None
    if entry[4] != "" and entry[4] != " " and entry[4] in guidelines:
        guideline = entry[4]
    else:
        guideline = None
    if entry[5] != "" and entry[5] != " " and entry[5] in components:
        target = entry[5].lower()
        if target == "storage":
            target = "object"
    else:
        target = None
    return testId, guideline, target


def linkChk(link, token):
    print("checking result with a test ID of: " + link.split("/")[-1])
    if not link:
        return False
    try:
        if " " in link:
            return False
        response = requests.get(
            link, headers={'Authorization': 'Bearer ' + token})
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print("Link check response_status_code=" +
                  str(response.status_code))
            return False
    except requests.exceptions as err:
        print(err)
        return False


def updateResult(apiLink, target, guideline, token, results_log):
    success = True
    with open(results_log, 'a') as logfile:
        logfile.write(str(datetime.datetime.now()) + ",")
        response = requests.post(apiLink + '/meta/shared', headers={
            'Authorization': 'Bearer ' + token}, data='true')
        if response.status_code != 201:
            print("Update shared status response_status_code=" +
                  str(response.status_code))
            logfile.write(apiLink + ",0,")
            success = False
        else:
            logfile.write(apiLink + ",1,")
        if ".json" not in guideline:
            guideline = str(guideline) + ".json"
        response = requests.post(apiLink + '/meta/guideline', headers={
            'Authorization': 'Bearer ' + token}, data=guideline)
        if response.status_code != 201:
            print("Update guideline response_status_code=" +
                  str(response.status_code))
            logfile.write(guideline + ",0,")
            success = False
        else:
            logfile.write(guideline + ",1,")
        response = requests.post(apiLink + '/meta/target', headers={
            'Authorization': 'Bearer ' + token}, data=target)
        if response.status_code != 201:
            print("Update target response_status_code=" +
                  str(response.status_code))
            logfile.write(target + ",0,")
            success = False
        else:
            logfile.write(target + ",1,")
        if success:
            print("test result updated. Verifying.")
            response = requests.put(apiLink, headers={
                'Authorization': 'Bearer ' + token},
                json={'verification_status': 1})
            if response.status_code != 201:
                success = False
            else:
                print("Test result verified.")
        logfile.write(str(int(success)) + '\n')
    return success


def main():
    linect = 0
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    parser.add_argument("--file", "-f", metavar='f', type=str, action="store",
                        required=True,
                        help="csv source for the data to use in updates")
    parser.add_argument(
        "--endpoint", "-e", metavar='e',
        type=str, action="store", required=True,
        help="the base URL of the endpoint. ex: http://examplerefstack.com/v1")
    parser.add_argument("--token", "-t", metavar="t", type=str,
                        action="store", required=True, help="API auth token")
    parser.add_argument("--logfile", "-l", metavar="l", type=str,
                        action="store", default="verification_results.csv",
                        help="name of logfile to output data into")
    result = parser.parse_args()
    infile = result.file
    logfile = result.logfile
    endpoint = result.endpoint
    token = result.token
    with open(infile) as f:
        for line in f:
            linect = linect + 1
            entry = line.split(",")
            testId, guideline, target = getData(entry)
            if testId is None or guideline is None or target is None:
                print(
                    "entry found at line " + str(linect) +
                    " cannot be updated and verified: entry incomplete.")
            else:
                apiLink = os.path.join(endpoint, 'results', testId)
                testResult = linkChk(apiLink, token)
                if testResult:
                    if testResult.get('verification_status'):
                        print(
                            "Result has already been verified; nothing to do.")
                    else:
                        print(
                            "Result link is valid. Updating result with ID " +
                            testId)
                        success = updateResult(apiLink, target, guideline,
                                               token, logfile)
                        if not success:
                            print("update of the results with the ID " +
                                  testId + " failed. please recheck your " +
                                  "spreadsheet and try again")
                else:
                    print("the test result " + testId +
                          " cannot be verified due to a broken result link.")


main()
