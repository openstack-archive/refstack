==========================================
Example Spec - The title of your blueprint
==========================================

https://blueprints.launchpad.net/refstack/+spec/test-result-json-schema

Refstack accepts connections from the refstac-client to post test results
for storage and scoring. Test results are in json and follow a simple
format. However there is no defined schema for the test results, allowing
for a greater possibility of invalid or malicious data to be injected
into the refstack database. This spec proposes the creation of a json
schema that can be used by client developers to generate their own valid
test results. The spec will also be used by the server to validate
incoming test results.

Problem description
===================

* Refstack accepts test results in json format. However, there is no
  explicit definition of the structure of this json data.

* Data sent to the Refstack server is not validated against any schema,
  increasing the possibility of invalid or malicious data.

* Clients developers do not have a specific schema to develop against.


Proposed change
===============

This change proposes the following additions:

* A json schema file to capture the format of the test results.

* Validation of incoming results against the json schema in Refstack.

Alternatives
------------

Another alternative is manually writing code to validate test results.
This schema does not preclue that alternative, but by creating and
validating against a schema we take advantage of existing libraries
and reduce the possiblity of introducing unintended parsing errors.

Data model impact
-----------------

This proposed change has two impacts on the data model:

* It introduces a schema that must be maintained and versioned
  against the current data model.

* It adds an additional level of validation to the 'create' operation
  of the CRUD model. Since running a test is a long operation this
  addition level of complexity will not have an impact on application
  performance.

* No database migrations will be necessary.

* A static page to serve the schema will be necessary.

REST API impact
---------------

The v1 api must be modified to validate test results. The modification
will result in an addition to behavior on the API with no changes
to the user-facing endpoint.

**description:** Receive tempest test result from a remote test runner. 
This function expects json formated pass results.
Update to the api described at:
https://github.com/stackforge/refstack/blob/master/specs/approved/api-v1.md

**url:** post /v1/results

**failed response:** http:400 - Malformed data.

    {
     'message': 'Malformed json data, see /v1/results/schema'
    }

**url:** get /v1/results/schema

**valid response:** http:200 schema.json file

No invalid responses. No accepted parameters.

Security impact
---------------

This change is intented to improve the security of the application
by introducing data validation. No data-changing apis are
introduced.

Notifications impact
--------------------

No known notification impacts.

Other end user impact
---------------------

End users may experience client failures if their client does not produce
valid json.

Performance Impact
------------------

This change introduces a validation step to the POST process. The additional
time used to validate the data is very small compared to the time taken
to generate data through cloud testing. The timing impact is negligible
in the context of the upload use case.

Other deployer impact
---------------------

This change will take immediate effect after being merged.

Developer impact
----------------

No additional developer impact.

Implementation
==============

This change will be implemented as a validation funtion in the API POST
pipeline. It will essentially be middleware that takes the input data,
validates the results, and sends back a positive or a negative result.
If the result is negative, the 400 response will be returned.
If the result is positive, the data processing will continue as normal.

Assignee(s)
-----------

Primary assignee:
    hogepodge

Work Items
----------

* Write json schema
* Write json schema GET endpoint
* Implement validation on results POST endpoint.
* Implement unit tests for validation and endpoint.

Dependencies
============

No additional dependencies will be added.

Testing
=======

To the TestRefStackApi class the following tests will be added:
* test_results_valid_data
* test_results_invalid_data

These results will confirm both positive (200) and negative (400) results.

To the unit tests the validator function will be tested:
* test_valid_data
* test_invalid_data
* test_empty_data

These results will provide three modes of schema validation.

Documentation Impact
====================

Documentation will be updated to link to current schema.

References
==========

No additional references.
