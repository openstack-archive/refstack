Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/vendor-result-validation

Requirement document: https://goo.gl/bvo4FG

Data model document: https://goo.gl/zWYnoq

Based on the blueprint and requirement documents listed above, this
specification is among a group of specifications that are defined for RefStack
to implement the vendor registration process.


Problem description
===================

RefStack needs to allow management of the vendor entity to a group of users not
just the users who create the vendors. This specification defines the REST APIs
needed to manage the users in a vendor.


Proposed change
===============

Add new REST APIs to support the following:

* List users in vendor

  Only foundation admins or admins in this vendor can request to get a list of
  the users belong to this vendor.

* Add user to vendor

  Only foundation admins or admins in this vendor can add a user to a vendor.

* Remove user from vendor

  Only foundation admins or admins in this vendor can remove a user from a
  vendor.  In addition, a user can remove himself/herself from a vendor.


Alternatives
------------

Since RefStack currently does not expose the "group" entity to the end users,
user management REST APIS are provided at the vendor level.  In the future, if
RefStack decides to support "group" management, then the APIs defined in this
specification can be updated by replacing the "vendor" entity with the "group"
entity.


Data model impact
-----------------

None

REST API impact
---------------

The following REST APIs will be added to RefStack.

**List users in vendor**

* Description:

  This API will be used by the OpenStack Foundation and vendor
  admins to list the users of a vendor. Note: currently the number of users
  in a vendor is expected to be small, no filter option will be implemented.
  However, in the future, as the number of user increases, RefStack may want
  to add filter options (such as filtering by name) to limit the amount of
  returned data.

* Method type: GET

* URI: v1/vendors/{vendor_id}/users

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
  | vendor_id     | URI   | csapi:UUID   | Vendor ID to retrieve user list.  |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  .. parsed-literal::
   {
      "users": [
         {
            "fullname" : "John Doe",
            "email" : "john_doe@compay1",
            "openid" : "https://openstackid.org/john.doe"
         },
         {
            "fullname" : "Jane Roe",
            "email" : "jane_roe@compay2",
            "openid" : "https://openstackid.org/jane.roe"
         },
        ......
      ]
   }


**Add user to vendor**

* Description:

  This API will be used by the OpenStack Foundation and vendor
  admins to add a user to a vendor.

* Method type: PUT

* URI: v1/vendors/{vendor_id}/users/{encoded_openid}

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
  | vendor_id     | URI   | csapi:UUID   | Vendor ID to add user to.         |
  +---------------+-------+--------------+-----------------------------------+
  | encoded_openid| URI   | xsd:string   | Base64 encoded user's OpenStack   |
  |               |       |              | OpenID                            |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data: N/A


**Remove user from vendor**

* Description:

  This API will be used by the OpenStack Foundation and vendor
  admins to remove a user from a vendor.

* Method type: DELETE

* URI: v1/vendors/{vendor_id}/users/{encoded_openid}

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
  | vendor_id     | URI   | csapi:UUID   | Vendor ID to remove user from.    |
  +---------------+-------+--------------+-----------------------------------+
  | encoded_openid| URI   | xsd:string   | Base64 encoded user's OpenStack   |
  |               |       |              | OpenID                            |
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
