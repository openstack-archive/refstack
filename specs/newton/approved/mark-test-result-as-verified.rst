====================================
Mark Test Result as Verified
====================================

Launchpad blueprint:

* https://blueprints.launchpad.net/refstack/+spec/certification-test-record

This specification defines the processes and mechanisms to mark a test result
as "verified for OpenStack Powered Logo application".


Problem description
===================

Currently, there is no mechanism to identify test results that are used by
the OpenStack Foundation (OSF) for OpenStack Powered Logo application.  At the
present, the test result URL links are sent to the OSF by the vendors per the
instructions described in the "How to Run the Tests" section of the
http://www.openstack.org/brand/interop/ site.

RefStack should provide a mean for OSF admins to mark a test result as
"verified for OpenStack Powered Logo application".

RefStack interprets OSF/DefCore requirements as following:

* The marked test results should be easily identified.
* The marked test results can not be deleted or updated.
* Only OSF admins can mark/umark a test.

Proposed change
===============

* Add a new field named "verification_status" to the "test" table.  Detailed
  information about this field can be found in the "Data model impact" section.

* Marking a test result record

  * Only interop admins can make updates to the verification_status field. For
    the https://refstack.openstack.org/#/ website, interop admins will be
    someone from the OSF.

  * Only a test result which has been shared and associated to a Guideline and
    Target Program can be marked as verified.

  * Once a test result is marked as verified, only interop admins can unmark
    the test.

  * Test results that are marked as verified cannot be deleted or updated.

  * A new API will be added to manage the verification_status field. Detailed
    information about the API can be found in the "REST API impact" section.

Alternatives
------------

Alternatively, we can use the existing test "meta" table to mark a test result.
This can be done by adding a key-value pair to the "meta" table, with key name
as "verification_status".  Following are the reasons why this implementation is
not chosen.

* Filtering/searching for marked data may not be as efficient.
* Marked tests can not be identified from the "test" table.


Data model impact
-----------------

Add a new column named "verification_status" to the existing "test" table.

+------------------------+-------------+----------+
| Column                 |   Type      |          |
+========================+=============+==========+
| verification_status    | int(11)     |          |
+------------------------+-------------+----------+

The verification_status column will store the pre-defined constants (enum) with
descriptive names as follows:

* 0 = not verified
* 1 = verified


REST API impact
---------------

The "Update result" REST API will be added to RefStack.  The "List results"
and "Show result details" REST APIs will be modified.

**Update result**

* Description:

  This API will be used to make updates to a test entry of the "test" table.
  Although the test owner, interop or vendor admins should be able to make
  updates to a rest record, extra checking must be implemented to ensure that
  only interop admins can mark or unmark a test.


* Method type: PUT

* URI: v1/results/{result_id}/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)
  * Forbidden (403)

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
          "required": []
       }
    }

  **Note**

  * The verification_status column will store a set of pre-defined constants
    (enum) with 0 = not verified, 1 = verified, etc.
  * Request to update the "verification_status" field will return
    "Forbidden(403)" if the requester is not an interop admin.

* JSON schema definition for the response data: N/A

**List results**

* Description: (No update)

* Method type: GET (No update)

* URI: v1/results/ (No update)

* Normal Response Codes: (No update)

* Error Response Codes: (No update)

* Request parameters:

  Add the following parameter to the existing ones:

  +---------------------+-------+----------+---------------------------------+
  | Parameter           | Style | Type     | Description                     |
  +=====================+=======+==========+=================================+
  | verification_status | query | xsd:int  | Pre-defined constants.          |
  | (optional)          |       |          | Not verified = 0                |
  |                     |       |          | Verified = 1                    |
  +---------------------+-------+----------+---------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  Update to add verification_status to the response body.

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
             verification_status : 0
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
             verification_status : 1
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

  Update to add verification_status to the response body.

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


Work Items
----------

* Add the defined additional field to the "test" table.
* Develop business and UI code to enable marking a test result.


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
