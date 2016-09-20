=============================================
Test Results to Vendor Products Association
=============================================

Launchpad blueprint:

* https://blueprints.launchpad.net/refstack/+spec/result-listing-page
* https://blueprints.launchpad.net/refstack/+spec/marketplace-product-model

This specification defines the processes and mechanisms to associate test
results to vendor products.

Problem description
===================

So far, community test results are shared to the public anonymously, with no
linkage to users, vendors or products.  DefCore, OpenStack Foundation (OSF)
and community user feedback revealed strong interest in enabling RefStack to
show the results with linkage to vendors, products and test statuses. This is
especially important for those test results that were used for official
OpenStack Powered Logo applications.

With the recent implementation of vendor and product registration process, it
is now possible to associate a particular test result record to a vendor's
product of a particular version.

**Note**

Test results are not associated directly to vendors. Test results are
associated to products which belong to vendors.  A product may have many
versions.

RefStack interprets OSF/DefCore requirements as following:

* Vocabulary:

  * product version: a product version is a version of a product.
  * product vendor: a product vendor is a vendor who owns the product.

* Model:

  * A product version can be used to deploy many clouds.
  * A product version can have many tests.
  * Test results will be associated to product versions (not products).

* Use cases:

  * Only the user who uploads the result and is also an admin of the product
    vendor or an interop admin can associate a test result to a product
    version.
  * Once a test is associated to a product version, only the admins of the
    product vendor or interop admins can perform CRUD operations on the test
    result.


Proposed change
===============

* Add a new columns to the "test" table in the database:

  * **product_version_id**:  this field stores the product version ID that the
    test run is associated to.

* Associate a test result to a product

  * The association must be initiated by a user who creates the test result
    record and is an admin of the vendor which owns the product.  The
    association is done by updating the product_version_id field of the test
    result with the ID of the product version from the "version" table.

  * Once a test result is associated to a product version, the test result can
    not be deleted until it is disassociate from a product.

  * Once a test result is associated to a product version, only interop
    (i.e. RefStack site) admins or vendor admins can manage the test result
    (e.g. making decision of sharing the test result record).

  * A product version can't be deleted if there are tests associated to it.

  **Note**

  Currently, RefStack has not implemented "user role" to differentiate the
  roles of users in a "user group".  As such, at this time, all users in a
  "user group" are admin users.

Alternatives
------------

An alternative method to associate a test record to a product is by matching
values of the "cpid" field (in the "version" table) and the "cpid" field (in
the "test" table).  The major concern and shortcomings of this option are as
follows:

* The "cpid" field is a user input parameter, therefore it is not guarantee to
  be unique.

* The cpid fields may be identical for test results run by different users
  against the same public cloud instance.

* A product may have many cloud instances which are identified by different
  cpids.


Data model impact
-----------------

Add a new column named "product_version_id" to the existing "test" table.
This field can be null.

+------------------------+-------------+----------+
| Column                 |   Type      |          |
+========================+=============+==========+
| product_version_id     | varchar(36) |   FK     |
+------------------------+-------------+----------+

Note: The user input product_version_id must exist in the "version" table.

REST API impact
---------------

The following REST APIs will be modified.

**Update result**

* Description:

  This API will be used to make update to a test entry of the "test" table.
  To begin with, only the owner user who uploaded the test result, can make
  update to the product_version_id filed.  Once a test is associated to a
  product version, only interop or vendor admins can make updates to a test
  result.

* Method type: PUT

* URI: v1/results/{result_id}/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Forbidden (403)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | result_id     | URI   | csapi:UUID   | Test result ID for marking.       |
  +---------------+-------+--------------+-----------------------------------+


* JSON schema definition for the body data:

  .. parsed-literal::
    {
       {
          "verification_status" : 1,
          "product_version_id": "85346866-307f-4052-ba31-ff6270635e14",
          "required": []
       }
    }

  **Note**

  * Although the verification_status column is listed here for completeness of
    the API body schema, this field can only be updated by interop admin as
    described in spec https://review.openstack.org/#/c/343954/ .
  * Update request including the "verification_status" field will return
    "Forbidden(403)" if the requester is not an interop admin.

* JSON schema definition for the response data: N/A

**List results**

* Description: (No update)

* Method type: GET (No update)

* URI: v1/results/ (No update)

* Normal Response Codes: (No update)

* Error Response Codes: (No update)

* Request parameters: (No update)

  Add the following parameter to the existing ones:

  +---------------------+-------+-------------+---------------------------------+
  | Parameter           | Style | Type        | Description                     |
  +=====================+=======+=============+=================================+
  | product_version_id  | query | xsd:string  | Only return the test records    |
  | (optional)          |       |             | belonging to this               |
  |                     |       |             | product_version_id.             |
  +---------------------+-------+-------------+---------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  Update to add product_version_id to the response body.

  .. parsed-literal::
    {
       pagination: {
          current_page: 6,
          total_pages: 37
       },
       results: [
          {
             url: "https://refstack.openstack.org/#/results/7943e04a-2b95-453c-b627-8a24b2c6faa0",
             created_at: "2016-07-25 02:24:34",
             meta: { },
             id: "7943e04a-2b95-453c-b627-8a24b2c6faa0",
             duration_seconds: 0,
             verification_status : 0,
             product_version_id: ""
          },
          {
             url: "https://refstack.openstack.org/#/results/91ae10c5-ecf5-4823-81d4-09836dc212cf",
             created_at: "2016-07-13 18:37:53",
             meta: {
                shared: ""true"",
                target: "compute",
                guideline: "2016.01.json"
             },
             id: "91ae10c5-ecf5-4823-81d4-09836dc212cf",
             duration_seconds: 6037,
             verification_status : 1,
             product_version_id: "68668534-307f-4052-ba31-ff6270635e14"
          },
          ........
       ]
    }

**Show result details**

* Description: (No update)

* Method type: GET (No update)

* URI: v1/results/{result_id} (No update)

* Normal Response Codes: (No update)

* Error Response Codes: (No update)

* Request parameters: (No update)

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  Update to add product_version_id to the response body.

  .. parsed-literal::
     {
       user_role: "user",
       created_at: "2016-07-13 18:37:53",
       meta: {
          shared: ""true"",
          target: "compute",
          guideline: "2016.01.json"
       },
       id: "91ae10c5-ecf5-4823-81d4-09836dc212cf",
       duration_seconds: 6037,
       verification_status : 1,
       product_version_id; "68668534-307f-4052-ba31-ff6270635e14",
       results: [
          "tempest.api.compute.certificates.test_certificates.CertificatesV2TestJSON.test_create_root_certificate",
          "tempest.api.compute.certificates.test_certificates.CertificatesV2TestJSON.test_get_root_certificate",
          ......
       ]
    }


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
  Andrey Pavlov

Other contributors:
  TBD

Work Items
----------

* Add the defined additional field to the "test" table.
* Develop business and UI code to enable association of a test result to a
  product.


Dependencies
============

None

Testing
=======

* Add unit tests to test the newly added code.


Documentation Impact
====================

None


References
==========

None
