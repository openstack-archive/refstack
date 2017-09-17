=============================================
Subunit Data Management API
=============================================

Launchpad blueprint:

* https://blueprints.launchpad.net/refstack/+spec/subunit-data-api

This specification describes an expansion of the refstack api which, when
complete, will allow for the upload and management  of subunit data files
to a RefStack server.

Problem description
===================

The current RefStack API allows for the upload, management, and verification
of test results by server administrators. These capabilities, though
sufficient for the current scope of RefStack, will need an API expansion in
order to allow for similar data management of subunit data results. This
expansion will enable those organizations looking to achieve a greater degree
of interoperability to securely share the details of test runs with the
Foundation so as to get assistance with getting their OpenStack instance to
successfully meet interop standards.


Proposed change
===============

**Add new API functionality to the RefStack v1 API**

  * Upload new subunit data- nonadmin capability

  * Link new subunit data to a corresponding existing test result-
    nonadmin capability

  * Delete subunit data- admin/owner capability

  * Show subunit data for a given test result- admin/owner capability



Note that, amongst the additions to the table that stores test results,
there is no added field intended for the storage of a subunit result id.
This is because, as per the spec defining the changes needed to upload and
utilize subunit data, the current plan is to link the two entries via the
metadata table.

Alternatives
------------

* If subunit2sql takes too long to perform the aforementioned operations,
  using asynchronous processing and upload may prove to be a better option.
  For now though, it appears as though synchronous operations will be possible
* Possibly require subunit data to be converted into json before being passed
  in for upload

Data model impact
------------------

This API will interface with subunit2sql, which will add several tables into
the RefStack database. Though these have been laid out already in the general
subunit data import spec, for the sake of thoroughness, here they
are again:::

 --------------------------------------
 |               tests                |
 --------------------------------------
 |   id           |  String(256)      |
 |   test_id      |  String(256)      |
 |   run_count    |  Integer          |
 |   failure      |  Integer          |
 |   run_time     |  Float            |
 --------------------------------------

 ----------------------------------------
 |              runs                    |
 ----------------------------------------
 |  id            |  BigInteger         |
 |  skips         |  Integer            |
 |  fails         |  Integer            |
 |  passes        |  Integer            |
 |  run_time      |  Float              |
 |  artifacts     |  Text               |
 |  run_at        |  DateTime           |
 ----------------------------------------

 ---------------------------------------------------
 |                    test_runs                    |
 ---------------------------------------------------
 |  id                      |  BigInteger          |
 |  test_id                 |  BigInteger          |
 |  run_id                  |  BigInteger          |
 |  status                  |  String(256)         |
 |  start_time              |  DateTime            |
 |  start_time_microseconds |  Integer             |
 |  stop_time               |  DateTime            |
 |  stop_time_microseconds  |  Integer             |
 |  test                    |  Test                |
 |  run                     |  Run                 |
 ---------------------------------------------------

 -------------------------------------------
 |            run_metadata                 |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  run_id        |  BigInteger            |
 |  run           |  Run                   |
 -------------------------------------------

 -------------------------------------------
 |          test_run_metadata              |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  test_run_id   |  BigInteger            |
 |  test_run      |  TestRun               |
 -------------------------------------------

 -------------------------------------------
 |            test_metadata                |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  test_id       |  BigInteger            |
 |  test          |  Test                  |
 -------------------------------------------

 -------------------------------------------
 |            attachments                  |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  test_run_id   |  BigInteger            |
 |  label         |  String(255)           |
 |  attachment    |  LargeBinary           |
 |  test_run      |  TestRun               |
 -------------------------------------------


REST API impact
---------------

The current plan, as briefly outlined above, is to make the following
additions to the current API:

**Upload subunit data**

* Description:

  This capability will be used to upload the subunit data of a test result
  that is not already in the database. It will do so in a few steps. First,
  it will take the subunit file open it, and convert it to v2 stream format
  (refstack-client outputs a subunit v1 file). Then, it will check to make
  sure the data is not already stored in the database, and if there is no
  record matching the data stored in the passed-in file, the api should then
  use subunit2sql to insert the subunit data into the appropriate fields, as
  well as inserting using the parsed data to insert a new entry into the
  refstack "runs" table using the existing refstack api utilities. This may
  seem a bit complicated for an upload function, but the goal in doing this
  all in one fell swoop is to ensure that no subunit data is ever uploaded
  that is not connected to some test result. Uploading subunit data will not
  require admin privileges.

* Method Type: POST

* URI: v1/subunit/

* Normal Response Codes:

  * Created (201)

* Error Response Codes:

  * Bad Request (400)
  * Not found (404)

* Request parameters: N/A

* JSON schema definition for the body data:

  .. parsed-literal::
    {
        {
            'subunit_data': <subunit data file>
        }
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
        'subunit-uuid': 'subunit2sql-defined run id',
        'result-id': 'result id'
    }


**Link subunit data to a corresponding existing test result**

* Description:

  This will allow for the linking of a new, unadded set of subunit data
  to data a test result already existing in the database. It will do
  so by converting the contents of the given file to a subunit v2 stream,
  then using the stream to generate a corresponding test result,
  and then comparing that to the passed in test result. If the
  generated result and the stored result correspond to one another,
  it should insert the subunit data into the database and link the two
  entries via a key value pair in RefStack's meta table. The two keys I
  plan to use are the subunit data's uuid and the test result's id.
  Because the validity of the link is easily verifiable, this action will
  not be one that requires admin privileges.

* Method Type: PUT

* URI: v1/subunit

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not Found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | result_id     | URI   | csapi:UUID   | test result ID to link to         |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
        'subunit data': <subunit data file>
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
      'uuid': 'subunit2sql-defined run id',
      'id': 'refstack test result id'
    }

**Delete subunit data entry**

* Description

  This utility will be used to delete subunit data from the RefStack
  database. Foundation and vendor admins, along with entry owners will
  be able to delete subunit data entry.

* Method type: DELETE

* URI: v1/subunit/{id}

* Normal Response Codes:

  * No content (204)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Forbidden (403)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | id            | URI   | csapi:UUID   | ID to be removed.                 |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data: N/A

**Show subunit data**

* Description

  This utility will be used to list the subunit data that has been
  uploaded into the RefStack database. This action will be available
  to vendor and Foundation admins only. A specific subunit data entry
  can be selected and viewed using the result_id parameter. It will do
  so in two steps. First, it will take the given test result id, and
  reference refstack's meta table to find the corresponding subunit
  uuid. Then, it will use that uuid to GET the subunit data from the
  v1/subunit/{uuid} endpoint.

* Method type: GET

* URI: v1/subunit/{uuid}

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Forbidden (403)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | id            | URI   | csapi:UUID   | test result id to search for.     |
  +---------------+-------+--------------+-----------------------------------+


* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  .. parsed-literal::
    {
      'subunit-data:': {
        'run_at': 2017-08-16 18:34:58.367221Z
        'uuid': '4d7950cb-586e-407e-9acf-5b169825af98',
        'skips': 0,
        'fails': 1,
        'passes': 1,
        'run_time': 2060.7
        'artifacts': 'http://example-logs.log',
      }
      'tests': [
        {
          'id': '1
          'test_id': 'tempest.api.network.test_security_groups.SecGroupTest.test_create_security_group_rule_with_icmp_type_code'
          'run_count': 1
          'success': 1
          'failure': 1
          'run_time': 5.60538
        },
        {
          'test_id': ' tempest.api.compute.keypairs.test_keypairs_negative.KeyPairsNegativeTestJSON.test_create_keypair_with_empty_public_key',
          'run_count': 1,
          'success': 0,
          'failure': 1,
          'run_time': 0.10919,
        },
      ]
      'test_runs': [
        {
          'test_id': 1,
          'run_id': 1,
          'status': 'success',
          'start_time': 2017-08-16 07:21:56,
          'stop_time': 2017-08-16 07:22:02,
          'start_time_microsecond': 929341,
          'stop_time_microsecond': 534721,
        },
        {
          'test_id': 2,
          'run_id': 2,
          'status': 'fail',
          'start_time': 2017-08-16 07:13:34,
          'stop_time': 2017-08-16 07:13:35,
          'start_time_microsecond': 693353,
          'stop_time_microsecond': 726471,
        },
      ]
      'attachments': [
        {
          'test_run_id': 1,
          'label': '<some label>'
          'attachment': '<some link>'
        }
      ]
    }


**Delete Test Result**

* Description

  This modification to the v1/results/ endpoint's delete function will
  ensure that, when a test result is deleted, the corresponding subunit
  data is too. This is neccessary largely because, in our data model,
  subunit data should always be linked to an associated test result.

* Method type: DELETE

* URI: v1/result/{id}

* Normal Response Codes:

  * No content (204)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Forbidden (403)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | id            | URI   | csapi:UUID   | ID to be removed.                 |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data: N/A

Security impact
---------------

There has been some concern over the sharing of subunit data via the RefStack
API, and though they are largely based on a misinformation, this is part of
why so few of the API additions are nonadmin. For more details about this
discussion, please refer to the generalized spec for the upload and usage of
subunit tests.

Notifications impact
--------------------

None.

Other end user impact
---------------------

None.

Performance impact
------------------

None.

Other deployer impact
---------------------

None.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Megan Guiney

Other contributors:
  TBD

Work Items
----------

* Discuss, amend, and merge this spec
* Run subunit2sql performance tests
* add field to "test" table
* add subunit api functionity
* add subunit-adjacent test result api functionality


Dependencies
============

* subunit2sql and its dependencies will need to be installed
  during refstack server setup. As a result, puppet-refstack may
  need some adjustments.


Testing
=======

* Add unit tests to verify the proper functionality of the new API
  additions.


Documentation Impact
====================

* Add documentation to detail the usage and functionality of the
  new API additions.


References
==========
[1] https://github.com/openstack/refstack/blob/master/specs/pike/approved
    /upload-subunit-tests.rst
