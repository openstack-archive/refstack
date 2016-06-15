Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/vendor-result-validation

Requirement document: https://goo.gl/bvo4FG

Data model document: https://goo.gl/zWYnoq

Based on the blueprint and requirement documents listed above, this spec
defines the REST APIs needed to support the product registration process.


Problem description
===================

As RefStack implements the vendor and product registration process, additional
REST APIs are needed for management of the newly added entities.  This spec
will focus on the product management APIs.


Proposed change
===============

Add new REST APIs to to RefStack v1 API support the following:

* Create a product

  Any RefStack authenticated user can create a product.

* Delete a product

  Foundation admins or admins in this vendor can delete the product records.

* Update a product record

  Foundation admins or admins in this vendor can make update to the product
  records.

* List product

  All RefStack users can list (view) publicly available product records with
  limited details.  Foundation admins and vendor admins can retrieve full
  detail information of the products.


Alternatives
------------

Direct access to the database to retrieve test records. Open to suggestions.

Data model impact
-----------------

None

REST API impact
---------------

The following REST APIs will be added to RefStack.

**List products**

* Description:

  This API will be used to list the products in RefStack.  By default, the
  response will include all product records that the user has privilege to
  retrieve.  The result list will be sorted by names in alphabetical ascending
  order.  At the time of this writing, the number of products will be
  registered in RefStack is expected to be small.  Therefore,  no
  result-limiting features such as pagination or filtering is implemented.
  More sophisticated filter, sorting and pagination features may be added in
  the future.

  **Note:** A "list products with detail" REST API will also be added later.
  Foundation and vendor admins can use this API to obtain additional private
  product information such as product record created date, created by user,
  etc.

* Method type: GET

* URI: v1/products/

* Normal Response Codes:

  * OK (200)

* Error Response Codes:

  * Bad Request (400)

* Request parameters: N/A

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  This response may include all publicly shared and private product records
  that the requester has privilege to retrieve.

  .. parsed-literal::
    {
       "products": [
          {
             "id" : "95346866-307f-4052-ba31-ff6270635e14",
             "name" : "Product ABC",
             "description" : "My description",
             "product_id" : "7e0072fb-a3e9-4901-82cd-9a3a911507d8",
             "product_type" : 1,
             "public" : true,
             "type" : 0,
             "can_manage" : false,
             "organization_id" : "69346866-307f-4052-ba31-ff6270635e19"
          },
          {
             "id" : "78346866-307f-4052-ba31-ff6270635e19",
             "name" : "Product EFG",
             "description" : "My description",
             "product_id" : "8c9u72fb-a3e9-4901-82cd-9a3a911507d8",
             "product_type" : 0,
             "public" : true,
             "type" : 1,
             "can_manage" : false,
             "organization_id" : "87346866-307f-4052-ba31-ff6270635e19"
          },
          {
             "id" : "12346866-307f-4052-ba31-ff6270635e19",
             "name" : "Product HIJ",
             "description" : "My description",
             "product_id" : "987672fb-a3e9-4901-82cd-9a3a911507d8",
             "product_type" : 2,
             "public" : true,
             "type" : 0,
             "can_manage" : false,
             "organization_id" : "77346866-307f-4052-ba31-ff6270635e19"
          },
          ......
       ]
    }


**Show product details**

* Description: This API will be used to retrieve the detail information of a
  particular product.
* Method type: GET
* URI: v1/products/{id}

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
  | id            | URI   | csapi:UUID   | ID to retrieve data.              |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  The response data will be filtered depending on whether the requester is a
  foundation admin or an admin user of the vendor which owns the product.

  * Response for non-foundation or none-vendor admins:

    .. parsed-literal::
      {
         {
             "id" : "12346866-307f-4052-ba31-ff6270635e19",
             "name" : "Product HIG",
             "description" : "My description",
             "product_id" : "987672fb-a3e9-4901-82cd-9a3a911507d8",
             "product_type" : 2,
             "public" : true,
             "type" : 0,
             "can_manage" : false,
             "organization_id" : "77346866-307f-4052-ba31-ff6270635e19"
         }
      }

  * Response for foundation or vendor admin users:

    .. parsed-literal::
      {
         {
            "id" : "12346866-307f-4052-ba31-ff6270635e19",
            "name" : "Product HIG",
            "description" : "My description"
            "product_id" : "987672fb-a3e9-4901-82cd-9a3a911507d8",
            "product_type" : 2,
            "public" : true,
            "properties" : "some text"
            "created_at": "2016-02-01 08:42:25",
            "created_by_user": "john@abc.com",
            "updated_at": "2016-02-02 08:42:25",
            "type" : 0,
            "can_manage" : true,
            "organization_id" : "77346866-307f-4052-ba31-ff6270635e19"
         }
      }

**Create product**

* Description:

  This API will be used to create a product in RefStack.  Any RefStack
  authenticated user can create a product.  Per current RefStack design, a
  product must be owned by a vendor. Therefore, if a vendor owner is not
  specified at the time when the product is created, a default private vendor
  will be created with the requester being assigned as the newly created
  vendor's admin user.  By default, a product will be created as private.

* Method type: POST

* URI: v1/products/

* Normal Response Codes:

  * Created (201)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters: N/A

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "name" : "ABC",
       "description" : "My description",
       "product_type" : 2,
       "organization_id" : "95346866-307f-4052-ba31-ff6270635e14",
       "required": ["name", "product_type"]
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       "id" : "345676866-307f-4052-ba31-ff6270635f20"
    }

**Update product**

* Description:

  This API will be used to update the fields of a product in RefStack.  Only
  foundation admins or admin users of this vendor can perform update on a
  product record.

* Method type: PUT

* URI: v1/products/{id}

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
  | id            | URI   | csapi:UUID   | ID for update.                    |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       {
          "name" : "Product EFG",
          "description" : "My description",
          "product_id" : "987672fb-a3e9-4901-82cd-9a3a911507d8",
          "public" : true,
          "properties" : "some text",
          "required": []
       }
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       {
          "id" : "95346866-307f-4052-ba31-ff6270635e14",
          "name" : "Product EFG",
          "description" : "My description",
          "product_id" : "987672fb-a3e9-4901-82cd-9a3a911507d8",
          "product_type" : 2,
          "public" : true,
          "properties" : "some text",
          "created_at": "2016-02-01 08:42:25",
          "created_by_user": "john@abc.com",
          "updated_at": "2016-02-02 08:42:25",
          "type" : 0,
          "can_manage" : true,
          "organization_id" : "77346866-307f-4052-ba31-ff6270635e19"
       }
    }


**Delete product**

* Description:

  This API will be used to delete a product in RefStack. Foundation admins and
  admin users of this vendor can delete a product.

* Method type: DELETE

* URI: v1/products/{id}

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
  | id            | URI   | csapi:UUID   | ID to be removed.                 |
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
