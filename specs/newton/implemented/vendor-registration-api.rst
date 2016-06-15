Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/vendor-result-validation

Requirement document: https://goo.gl/bvo4FG

Data model document: https://goo.gl/zWYnoq

Based on the blueprint and requirement documents listed above, this spec
defines the REST APIs needed to support the vendor registration process.


Problem description
===================

As RefStack implements the vendor registration process, additional REST APIs
are needed for management of the newly added entities such as product and
vendor.  Two categories of REST APIs will be created, one for vendor management
(CRUD) and the other for product management. This spec will focus on the vendor
management API.

The new APIs will be added to RefStack v1 API.


Proposed change
===============

Add new REST APIs to support the following:

* Create a vendor

  Any RefStack authenticated user can create a vendor.  By default, the vendor
  is of type "private" vendor when it is created.

* Delete a vendor

  Only foundation admins can delete official vendors.  In addition, vendor
  admin users can delete own private/pending vendor.

* Update a vendor record

  Foundation admins or admins in this vendor can make update to the vendor
  records.

* List vendor

  All RefStack users can list (view) official vendor records with limited
  details.  Foundation admins can retrieve full detail records of all vendors.


Alternatives
------------

Direct access to the database to retrieve test records. Open to suggestions.

Data model impact
-----------------

None

REST API impact
---------------

The following REST APIs will be added to RefStack.

**List vendors**

* Description:

  This API will be used to list the vendors in RefStack.  By default, the
  response will include all vendor records that the user has privilege to
  retrieve.  This list will be sorted by names in alphabetical ascending
  order.  At the time of this writing, the number of vendor will be registered
  in RefStack is expected to be small.  Therefore,  no result-limiting features
  such as pagination or filtering is implemented.  More sophisticated filter,
  sorting and pagination features may be added in the future.

  **Note:** A "list vendors with detail" REST API will also be added later.
  Foundation and vendor admins can use this API to obtain more detail private
  vendor information such as vendor record created date, created user, etc.

* Method type: GET

* URI: v1/vendors/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)

* Request parameters: N/A

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  This response may include all official (public) vendors, the private and
  pending vendors that the requester has privilege to retrieve.

  .. parsed-literal::
    {
       "vendors": [
          {
             "id" : "95346866-307f-4052-ba31-ff6270635e14",
             "name" : "Vendor ABC",
             "description" : "My description",
             "type" : 3
          },
          {
             "id" : "78346866-307f-4052-ba31-ff6270635e19",
             "name" : "Vendor EFG",
             "description" : "My description",
             "type" : 1
          },
          ......
       ]
    }

  **Note:** The values of the "type" filed are a set of pre-defined constants
  (enum) depicting the type of vendors.  The constant definition can be found
  in https://github.com/openstack/refstack/blob/master/refstack/api/constants.py .

**Show vendor details**

* Description: This API will be used to retrieve the detail information of a
  particular vendor.
* Method type: GET
* URI: v1/vendors/{vendor_id}

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID to retrieve data.       |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  The response data will be filtered depending on whether the requester is a
  foundation admin or an admin user of this vendor.

  * Response for non-foundation or vendor admins:

    .. parsed-literal::
      {
         {
            "id" : "95346866-307f-4052-ba31-ff6270635e14",
            "name" : "Vendor ABC",
            "description" : "My description",
            "type" : 3
         }
      }

  * Response for foundation or vendor admin users:

    .. parsed-literal::
      {
         {
            "id" : "95346866-307f-4052-ba31-ff6270635e14",
            "name" : "Vendor ABC",
            "description" : "My description",
            "type" : 3,
            "created_at": "2016-02-01 08:42:25",
            "created_by_user": "john@abc.com",
            "updated_at": "2016-02-02 08:42:25",
            "properties" : "some text"
         }
      }

**Create vendor**

* Description:

  This API will be used to create a vendor in RefStack.  By default the vendor
  will be created as a private vendor.

* Method type: POST

* URI: v1/vendors/

* Normal Response Codes:

  * Created (201)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)

* Request parameters: N/A

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "name" : "ABC",
       "description" : "My description",
       "required": ["name"]
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       "id" : "95346866-307f-4052-ba31-ff6270635e14"
    }

**Update vendor**

* Description:

  This API will be used to update the fields of a vendor in RefStack.  Only
  foundation admins or admin users of this vendor can perform update on a
  vendor record.

* Method type: PUT

* URI: v1/vendors/{vendor_id}

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID for update.             |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       {
          "name" : "Vendor ABC",
          "description" : "My description",
          "properties" : "some text",
          "required": []
       }
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       {
          "id" : "95346866-307f-4052-ba31-ff6270635e14",
          "name" : "Vendor ABC",
          "description" : "My description",
          "type" : 3,
          "created_at" : "2016-02-01 08:42:25",
          "created_by_user": "john@abc.com",
          "updated_at" : "2016-02-02 08:42:25",
          "properties" : "some text"
       }
    }


**Vendor action API**

  The action API is used to perform an action on the vendor object.  The action
  is defined in the request body.


**Register as an official vendor**

* Description:

  This API will be used by the vendor admins to register a private vendor for
  foundation approval to become an official vendor.

* Method type: POST

* URI: v1/vendors/{vendor_id}/action

* Normal Response Codes:

  * OK (202)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID for update.             |
  +---------------+-------+--------------+-----------------------------------+
  | register      | plain | xsd:string   | Action to request registering a   |
  |               |       |              | private vendor to become an       |
  |               |       |              | official vendor.  vendor "type"   |
  |               |       |              | will change from "private" to     |
  |               |       |              | "pending"                         |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "register" : null
    }

* JSON schema definition for the response data: N/A


**Cancel submitted register request**

* Description:

  This API will be used by the vendor admins to cancel previously submitted register
  requests.

* Method type: POST

* URI: v1/vendors/{vendor_id}/action

* Normal Response Codes:

  * OK (202)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID for update.             |
  +---------------+-------+--------------+-----------------------------------+
  | cancel        | plain | xsd:string   | Action to request canceling  a    |
  |               |       |              | previously submitted register     |
  |               |       |              | request.                          |
  |               |       |              | Vendor "type" will change from    |
  |               |       |              | "pending" to "private".           |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "cancel" : null
    }

* JSON schema definition for the response data: N/A


**Approve to become an official vendor**

* Description:

  This API will be used by the foundation admins to apporove a vendor of type
  "pending" to become an official vendor.

* Method type: POST

* URI: v1/vendors/{vendor_id}/action

* Normal Response Codes:

  * OK (202)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID for update.             |
  +---------------+-------+--------------+-----------------------------------+
  | approve       | plain | xsd:string   | Action to approve a vendor of type|
  |               |       |              | "pending" to "official"           |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "approve" : null
    }

* JSON schema definition for the response data: N/A

**Deny to become an official vendor**

* Description:

  This API will be used by the foundation admins to deny a vendor of type
  "pending" to become an official vendor.

* Method type: POST

* URI: v1/vendors/{vendor_id}/action

* Normal Response Codes:

  * OK (202)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID for update.             |
  +---------------+-------+--------------+-----------------------------------+
  | deny          | plain | xsd:string   | Action to deny a vendor of type   |
  |               |       |              | "pending" to "official". Vendor   |
  |               |       |              | type will change from "pending" to|
  |               |       |              | "private".                        |
  +---------------+-------+--------------+-----------------------------------+
  | reason        | plain | xsd:string   | Reason for denial.                |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "deny" : null
       "reason" : "My reason for denial"
    }

* JSON schema definition for the response data: N/A


**Delete vendor**

* Description:

  This API will be used to delete a vendor in RefStack. Only foundation admins
  can delete an official (public) vendor.  Foundation admins and admin users of
  this vendor can delete a private or pending vendor.

* Method type: DELETE

* URI: v1/vendors/{vendor_id}

* Normal Response Codes:

  * No content (204)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | vendor_id     | URI   | csapi:UUID   | Vendor ID to be removed.          |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data: N/A

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
  Andrey Pavlov

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
