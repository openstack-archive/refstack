====================================
Product Version Data Model and API
====================================

Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/marketplace-product-model

Based on the requirements listed in the blueprint, this spec defines the
database and API updates needed to support the product model used by the
OpenStack Marketplace.


Problem description
===================

In RefStack, a product is an entry saved in the "product" table. Currently,
RefStack does not support the model where a product may have one to many
product versions.  RefStack needs to update its database and object models to
meet the product model described in the blueprint.

RefStack interprets OpenStack Marketplace product definition and requirement
as following:

* Model:

  * Each product will have one to many versions.

* Vocabulary:

  * product: a product is an entry on the marketplace website.  For example:
    "IBM Spectrum Scale for Object Storage" [1] is a product.

  * version: version is unique name/number denoting a particular state of a
    product.  A product may have one to many versions.  For example:
    "IBM Spectrum Scale for Object Storage" has release 4.1.1, 4.2.0, 4.2.1,
    etc. While a public cloud may have only one version.  In this case, the
    version name can be null. Note that the term version and release are used
    interchangeably.

* Use cases:

  * User can create a new product after log into to
    https://refstack.openstack.org/#/.
  * User can adds new versions to an existing product.

[1] https://www.openstack.org/marketplace/distros/distribution/ibm/ibm-spectrum-scale-for-object-storage


Proposed change
===============


* Add a new table named "product_version" and methods to access it.

  This table will store the version information of a product. Detailed
  information about this table is described in the "Data model impact"
  section.

* Add new REST APIs ( get/create/update/delete ) to operate on the product
  version resource.


**Note**

Currently, RefStack has not implemented "user role" to differentiate the roles
of users in a "user group".  As such, at this time, all users in a "user group"
would be admin users.

Alternatives
------------

There is no appropriate alternative found to model the "1 to N" relationship
between product and its versions.

There is suggestion that this can be achieved by simply adding a "version"
column to the "product" table.  This is the most simple implementation with
minimum changes.  Unfortunately, it does not support the required "1 to N"
relationship because an entry with user input product information will be
created each time.  This is regardless of whether the user wants to create a
new product or a new version for an existing product.

With this approach, each product is an entry in the "product" table with
columns: product_id, name, version (and many other columns that are not
relevant to this discussion).  While "product_id" is created uniquely by
the system, "name" and "version" are user input fields. A row with two users
input fields are created each time for a new product or a new version for an
existing product.


.. |reg|  unicode:: U+00AE .. REGISTERED SIGN

In the following examples, Are "ABC OpenStack\ |reg|." and "ABC OpenStack" one or two
different products?

* It could be one product because the users had made a mistake when creating a
  new version for the existing "ABC OpenStack\ |reg|." product.
* It could also be two products, since the 2 names are not the same.

Such kind of data integrity and consistency issues should be avoid whenever
possible with appropriate database design and/or bussiness layer code.

==========    ===================    =======
product_id    Name                   Version
==========    ===================    =======
11111         ABC OpenStack |reg|    v6.0
22222         ABC OpenStack          v7.0
33333         ABC OpenStack |reg|    v8.0
==========    ===================    =======

Data model impact
-----------------

* Add a product_version table

  +------------------------+-------------+----------+
  | Column                 |   Type      |          |
  +========================+=============+==========+
  | created_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted                | int(11)	 |          |
  +------------------------+-------------+----------+
  | updated_at             | datetime    |          |
  +------------------------+-------------+----------+
  | created_by_user        | varchar(128)| FK       |
  +------------------------+-------------+----------+
  | id                     | varchar(36) | PK       |
  +------------------------+-------------+----------+
  | version                | varchar(30) |          |
  +------------------------+-------------+----------+
  | product_id             | varchar(36) | FK       |
  +------------------------+-------------+----------+
  | cpid                   | varchar(36) |          |
  +------------------------+-------------+----------+


  ** Note **

  * The version field can be blank. This is to support the case where public
    cloud may have no version.
  * The combination of the version and product_id fields must be unique.
    This can be achieved by implementing a compound unique key of
    (product_id, version) as UniqueConstraint to provide some level of
    duplication protection.
  * cpid is the ID of a cloud which is deployed using this product version.
    cpid can be blank.


REST API impact
---------------

The following REST APIs will be added to RefStack.

**List product versions**

* Description:

  This API will be used to list all the versions of a product.

* Method type: GET

* URI: v1/products/{product_id}/versions

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
  | product_id    | URI   | csapi:UUID   | ID of a product.                  |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  This response may include versions of all publicly shared and private
  products that the requester has privilege to retrieve. Access checking for
  version is always done at the product level.

  .. parsed-literal::
    {
       "versions": [
          {
             "id" : "85346866-307f-4052-ba31-ff6270635e14",
             "version" : "v1",
             "product_id" : "7e0072fb-a3e9-4901-82cd-9a3a911507d8",
             "cpid" : ""
          },
          {
             "id" : "36846866-307f-4052-ba31-ff6270635e19",
             "version" : "",
             "product_id" : "9u9c72fb-a3e9-4901-82cd-9a3a911507d8",
             "cpid" : "69346866-307f-4052-ba31-ff6270635e19"
          },
          ......
       ]
    }


**Show product version details**

* Description: This API will be used to retrieve the detailed information of a
  product version.
* Method type: GET
* URI: v1/products/{product_id}/versions/{version_id}

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
  | product_id    | URI   | csapi:UUID   | ID of a product.                  |
  +---------------+-------+--------------+-----------------------------------+
  | version_id    | URI   | csapi:UUID   | ID of a product version.          |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data: N/A

* JSON schema definition for the response data:

  The response data will be filtered depending on whether the requester is an
  interop admin or an admin user of the vendor which owns the product.

  * Response for non-foundation or none-vendor admins:

    .. parsed-literal::
      {
         {
            "id" : "85346866-307f-4052-ba31-ff6270635e14",
            "version" : "v1",
            "product_id" : "7e0072fb-a3e9-4901-82cd-9a3a911507d8",
            "cpid" : ""
         }
      }

  * Response for foundation or vendor admin users:

    .. parsed-literal::
      {
         {
            "id" : "85346866-307f-4052-ba31-ff6270635e14",
            "version" : "v1",
            "product_id" : "7e0072fb-a3e9-4901-82cd-9a3a911507d8",
            "cpid" : ""
            "created_at": "2016-02-01 08:42:25",
            "created_by_user": "john@abc.com",
            "updated_at": "2016-02-02 08:42:25",
         }
      }

**Create product version**

* Description:

  This API will be used to create a product version. Only interop or vendor
  admins of the product can create a product version.

* Method type: POST

* URI: v1/products/{product_id}/versions

* Normal Response Codes:

  * Created (201)

* Error Response Codes:

  * Bad Request (400)
  * Unauthorized (401)
  * Not found (404)

* Request parameters:

  +---------------+-------+--------------+-----------------------------------+
  | Parameter     | Style | Type         | Description                       |
  +===============+=======+==============+===================================+
  | product_id    | URI   | csapi:UUID   | ID of a product.                  |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       "version" : "",
       "cpid" : "69346866-307f-4052-ba31-ff6270635e19",
       "required": ["version"]
    }


* JSON schema definition for the response data:

  .. parsed-literal::
    {
       "id" : "345676866-307f-4052-ba31-ff6270635f20"
    }

**Update product version**

* Description:

  This API will be used to update the fields of a product version in RefStack
  Only interop admins or admin users of the product vendor can perform update
  on a product version record.

* Method type: PUT

* URI: v1/products/{product_id}/versions/{version_id}

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
  | product_id    | URI   | csapi:UUID   | ID of a product.                  |
  +---------------+-------+--------------+-----------------------------------+
  | version_id    | URI   | csapi:UUID   | ID of a product version.          |
  +---------------+-------+--------------+-----------------------------------+

* JSON schema definition for the body data:

  .. parsed-literal::
    {
       {
          "version" : "",
          "cpid" : "69346866-307f-4052-ba31-ff6270635e19",
          "required": []
       }
    }

* JSON schema definition for the response data:

  .. parsed-literal::
    {
       {
           "id" : "85346866-307f-4052-ba31-ff6270635e14",
           "version" : "v1",
           "product_id" : "7e0072fb-a3e9-4901-82cd-9a3a911507d8",
           "cpid" : "69346866-307f-4052-ba31-ff6270635e19"
           "created_at": "2016-02-01 08:42:25",
           "created_by_user": "john@abc.com",
           "updated_at": "2016-02-02 08:42:25",
       }
    }


**Delete a product version**

* Description:

  This API will be used to delete a product version in RefStack. Interop admins
  and admin users of the product vendor can delete a product version.

* Method type: DELETE

* URI: v1/products/{product_id}/versions/{version_id}

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
  | product_id    | URI   | csapi:UUID   | ID of a product.                  |
  +---------------+-------+--------------+-----------------------------------+
  | version_id    | URI   | csapi:UUID   | ID of a product version.          |
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
  Paul Van Eck
  Andrey Pavlov

Other contributors:
  TBD

Work Items
----------

* Create the product version table.
* Create the newly APIs.
* Update RefStack UI to include product version information.


Dependencies
============

None


Testing
=======

* Add unit tests to verify newly developed code.


Documentation Impact
====================

None


References
==========

None
