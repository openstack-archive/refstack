This spec defines the REST APIs needed to support the retrieval of DefCore
Guideline files and the test lists included in these files.


Problem description
===================

The DefCore Guideline files contain many different types of test lists such as
required test lists, advisory test lists, etc.  Very often, these lists are used
by RefStack users to test only the tests that they are interested in.
For each Guideline file, there is a corresponding directory which holds files
that contain the required or flagged tests (see example [1]).  Since the test
lists in these files can change from time to time due to test name changes [2]
or addition of flagged tests [3], it is useful for RefStack to provide
REST APIs so that users can dynamically retrieve the test lists with the latest
updates in the Guideline files as needed.

[1] https://github.com/openstack/defcore/tree/master/2016.01
[2] https://review.openstack.org/#/c/290689/
[3] https://review.openstack.org/#/c/215263/

Proposed change
===============

RefStack to provide the REST APIs as described in the "REST API Impact" section
to retrieve the Guideline files and the test lists included in these files.


Alternatives
------------

Users to continue using the required and flagged test list files in the DefCore
repository.

Data model impact
-----------------

None

REST API impact
---------------

The following REST APIs will be added to RefStack.

**List DefCore Guideline files**

* Description:

  List the names of the DefCore Guideline files

* Method type: GET

* URI: v1/guidelines/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)

* Request parameters:

  N/A

* JSON schema definition for the body data:

  N/A

* Schema definition for the response data:

  .. parsed-literal::
    [
       "2015.03.json",
       "2015.04.json",
       ...
    ]


**Show Guideline file details**

* Description:

  This API will be used to retrieve the content of a
  DefCore Guideline file.

* Method type: GET

* URI: v1/guidelines/{name}

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  |   name        | URI   | xsd:string   | The name of the Guideline file    |
  |               |       |              | such as "2015.04".                |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  N/A

* JSON schema definition for the response data:

  See DefCore Guideline JSON schema
  https://github.com/openstack/defcore/tree/master/doc/source/schema


**List tests**

* Description:

  This API will be used to list the tests included in the Guideline. By default,
  this API will return all the tests included in the required, advisory,
  deprecated and removed categories.

* Method type: GET

* URI: v1/guidelines/{name}/tests

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | type          | query | xsd:string   | Type can be a comma separated list|
  | (optional)    |       |              | of required, advisory, deprecated |
  |               |       |              | and removed. Default is to        |
  |               |       |              | retrieve test list of all types.  |
  +---------------+-------+--------------+-----------------------------------+
  | alias         | query | xsd:string   | Set alias=true (default) to       |
  | (optional)    |       |              | include alias test names in the   |
  |               |       |              | response test list.               |
  |               |       |              | alias=false will exclude the alias|
  |               |       |              | test names.                       |
  +---------------+-------+--------------+-----------------------------------+
  | flag          | query | xsd:string   | Set flag=true (default) to include|
  | (optional)    |       |              | flagged test names in the         |
  |               |       |              | response test list.               |
  |               |       |              | flag=false will not include       |
  |               |       |              | flagged tests.                    |
  +---------------+-------+--------------+-----------------------------------+
  | target        | query | xsd:string   | Use this parameter to retrieve the|
  | (optional)    |       |              | test lists for a target program.  |
  |               |       |              | Current valid values include the  |
  |               |       |              | following:                        |
  |               |       |              |                                   |
  |               |       |              | - platform (default)              |
  |               |       |              | - compute                         |
  |               |       |              | - object-storage                  |
  +---------------+-------+--------------+-----------------------------------+

  **Note**

  More information about OpenStack Target Programs can be found at
  http://www.openstack.org/brand/interop/ .

  **Examples**

  * Get the required test list including alias and flagged tests.

    `v1/guidelines/2016.01/tests?type=required`

  * Get the required test list including alias but excluding flagged tests.

    `v1/guidelines/2016.01/tests?type=required&flag=false`

  * Get the required and advisory tests for the OpenStack Powered Compute
    program, including alias but excluding flagged tests

    `v1/guidelines/2016.01/tests?type=required,advisory&flag=false&target=compute`


* JSON schema definition for the body data:

  N/A

* Schema definition for the response data:

  The response is a straight list of tests so that users can immediately use the file
  as-is for testing with refstack-client.

  .. parsed-literal::
       tempest.api.compute.images.test_list_images.ListImagesTestJSON.test_get_image[id-490d0898-e12a-463f-aef0-c50156b9f789]
       tempest.api.compute.images.test_list_images.ListImagesTestJSON.test_list_images[id-fd51b7f4-d4a3-4331-9885-866658112a6f]
       ....

Security impact
---------------

None.

Notifications impact
--------------------

None.

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

Primary assignee:
  Paul Van Eck

Other contributors:
  TBD

Work Items
----------

* Create the REST APIs.


Dependencies
============

None


Testing
=======

None


Documentation Impact
====================

None


References
==========

None
