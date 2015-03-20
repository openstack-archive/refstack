..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=================================================
Add Test Records Retrieval API to Refstack v1 API
=================================================

StoryBoard https://storyboard.openstack.org/#!/story/2000212

This story proposes to add a new REST API that returns the test records
of the test results that have been uploaded to the Refstack server.


Problem description
===================

Currently, there is no API provided to retrieve the test records that the
users have uploaded to the Refstack server.  The test records do not
contain the actual results of the tests.  A test record only includes
test_id (result_id), date on which test was uploaded to refstack and
"cloud provider ID" (cpid) where the test results were collected.

The use cases for adding this API are derived from the mockup phase for
Refstack user interface experience.

Use Case 1: A UI dashboard that shows all test records that have been
uploaded to the Refstack server in the last number of days.

Use Case 2: A UI dashboard that shows the latest test records that have been
uploaded to the Refstack server by all cloud providers identified by
"cloud provider ID" (cpid).

Use Case 3: A UI that shows all test records uploaded by a cloud provider.

Proposed change
===============

Add an API to Refstack v1 API to retrieve test records stored in the
"tests" table of the Refstack database.  This API will need to support the
following optional filtering parameters:

* Ability to specify the number of returned records.
* Ability to only retrieve test records in a specified date range.
* Ability to retrieve test records for a specific cloud provider identified
  by its "Cloud Provider ID" (cpid).

Note: Currently, there is no user or vendor identity associated to the test
results.  The only association is with cpid.  As the user and vendor
information become available, this API needs to be updated to provide
filtering based on user and vendor identity.

Alternatives
------------

Direct access to the database to retrieve test records. Open to suggestions.


Data model impact
-----------------

None

REST API impact
---------------

Add a new API with the following specification.

* Description: This API will be used to retrieve the test run records that
  were uploaded to the Refstack database.
* Method type: GET
* URI: v1/results/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * BadRequest (400)
  * Unauthorized (401)
  * Not found (404)

* Parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | start_date    | query | xsd:date     | Only retrieve data uploaded from  |
  | (optional)    |       |              | this date.  ISO 8601 date format  |
  |               |       |              | YYYY-MM-DD                        |
  +---------------+-------+--------------+-----------------------------------+
  | end_date      | query | xsd:date     | Only retrieve data uploaded up to |
  | (optional)    |       |              | this date.  ISO 8601 date format  |
  |               |       |              | YYYY-MM-DD                        |
  +---------------+-------+--------------+-----------------------------------+
  | cpid          | query | xsd:string   | Only return the test records      |
  | (optional)    |       |              | belonging to this cpid.           |
  +---------------+-------+--------------+-----------------------------------+
  | page          | query | xsd:int      | Page number to retrieve result    |
  | (optional)    |       |              | records.  Default is page=1 which |
  |               |       |              | contains the latest number of     |
  |               |       |              | result records uploaded.  The     |
  |               |       |              | number of records per page is     |
  |               |       |              | configurable via the refstack.conf|
  |               |       |              | file.                             |
  +---------------+-------+--------------+-----------------------------------+



* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       {'test_id' : '95346866-307f-4052-ba31-ff6270635e14',
        'created_at': '2015-02-02 23:42:25',
        'cpid' : '043ef631f4204935a59c9ba573f0e111'
       },
       {'test_id' : '95346866-307f-4052-ba31-ff6270635e15',
        'created_at': '2015-03-02 23:42:25',
        'cpid' : '043ef631f4204935a59c9ba573f0e122'
       }
       ......
    }

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee: Vladislav Kuzmin

Other contributors: Catherine Diep

Work Items
----------

* Create new API functions in the various layers.


Dependencies
============

None


Testing
=======

Require API unit tests for each call and expected response.


Documentation Impact
====================

All API functions will have sphinx compatible doc tags reflecting actual usage.


References
==========

None
