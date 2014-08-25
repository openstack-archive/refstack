=================================================
Understanding the DefCore JSON Schema
=================================================

This folder contains DefCore committee managed files that provide trusted guidance for the OpenStack community.

Assets for each release are tracked in dedicated subdirectories so JSON schema may change per release if needed.

NOTE: Changes to file requires approval of the DefCore committee chair(s).


DefCore Process Flow
====================

See: https://wiki.openstack.org/w/images/6/68/DefCoreProcessFlow.pdf 

Terminology
====================

See: https://wiki.openstack.org/wiki/Governance/DefCoreLexicon 

The JSON files have a specific schema to support 

.. code-block:: json

  { "release": "havana",
    "schema": "1.0",
    "criteria" : { 
        "atomic" : { "Description" : "blah blah blah",
        "name" : "Atomic", 
        "weight": 8
        },
    "capabilities": {
      "example-cap" : { "achievements" : [ "deployed",
            "future",
            "complete"],
        "admin" : true,
        "core" : false,
        "description" : "Helpful Description",
        "flagged" : [  ],
        "name" : "Friendly Short Name",
        "tests" : [ "tempest.api.project.file.class.test_name" ]
      },

Schema Explanation:
-------------------

* release: provides the release described in the JSON file
* schema: version of the schema
* criteria: block describing the scoring criteria for the release
   * criteria/[id]: block for a specific criteria (using an ID)
   * criteria/[id]/name: friendly name for the criteria
   * criteria/[id]/description: longer description for the criteria
   * criteria/[id]/weight: weight applied.  All criteria together should = 100
* capabilities: block describing all the capabilities identified for the release
   * capabilities/[id]: block for a specific capability (using an ID)
   * capabilities/[id]/name: friend name for the capability
   * capabilities/[id]/description: longer description for the capability
   * capabilities/[id]/core: boolean set by Board if capability is required
   * capabilities/[id]/admin: boolean set by PTL if capability is for admin use
   * capabilities/[id]/achievements: list of criteria passed for this capability (set by Board)
   * capabilities/[id]/tests: list of tests included in the capability (set by PTL)
   * capabilities/[id]/flagged: tests that have been excluded for this capability (set by Board)

Ownership for Changes
=====================

TC/PTL
---------------------
1. Capabilities Description
1. Capabilities Test List

DefCore
---------------------
1. Flagged Tests
1. Capabilities "Score
1. Criteria Names and Descriptions


