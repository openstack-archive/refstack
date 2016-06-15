Database Tables for Vendor Registration Support
===============================================

Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/vendor-result-validation

Requirement document: https://goo.gl/bvo4FG

Data model document: https://goo.gl/zWYnoq

Based on the blueprint and requirement documents listed above, this spec is the
first of a series of specifications that will be defined for RefStack to
implement the vendor registration process.  This spec will mainly focus on
the data model aspect of the vendor registration implementation.


Problem description
===================

As RefStack implements the vendor/product registration process, additional
database tables are needed to store the newly added entities such as vendor,
cloud provider, etc.  Based on the object model described in the requirement
document, this spec defines the tables and the basic methods/functions needed
to manage them.


Proposed change
===============

The following tables will be added to the RefStack database:

* A table named "organization"

  The organization table will store the data representing entities such as
  Software Vendors, Cloud Operators, OpenStack Foundation, etc.  The various
  types of entities stored in this table will be differentiated by the
  values stored in the "type" column. These values are pre-defined in a set
  of constants (enum) with descriptive names. For example: 1 = foundation,
  2 = official_vendor, 3 = private_vendor, etc.  There will be only one
  organization with the type of "foundation" in a RefStack instance.  This
  organization will be created by the RefStack admin.

* A table named "product"

  This table will contain the product information. Each product must be owned
  by a vendor.  A "product_type" column will be used to identify the different
  types of products. The types of products are pre-defined constants (enum)
  with descriptive names as defined in the OpenStack Marketplace
  ( http://www.openstack.org/marketplace/). For example: 1 = distro,
  2 = public_cloud, 3 = hosted_private_cloud, etc.

Details about these tables are described in the "Data model impact" section.

The following methods will be added:

* Methods to add/remove a vendor and its associated attributes.
* Methods to add/remove a product and its associated attributes.

Alternatives
------------

Auditability is not included in the current implementation. RefStack should
require at least some logging/auditing capability. While RefStack can add richer
auditability features overtime incrementally, at the minimum an updated_by_user
column should be added to the tables to log the last update activity made on an
organization or product entity.

Open to other suggestions.

Data model impact
-----------------
The following tables will be added to the RefStack database.

* "organization" table

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
  | name                   | varchar(80) |          |
  +------------------------+-------------+----------+
  | description            | text        |          |
  +------------------------+-------------+----------+
  | type                   | int(11)     |          |
  +------------------------+-------------+----------+
  | group_id               | varchar(36) | FK       |
  +------------------------+-------------+----------+
  | properties             | text        |          |
  +------------------------+-------------+----------+


* "product" table

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
  | name                   | varchar(80) |          |
  +------------------------+-------------+----------+
  | description            | text        |          |
  +------------------------+-------------+----------+
  | product_id             | varchar(36) |          |
  +------------------------+-------------+----------+
  | type                   | int(11)     |          |
  +------------------------+-------------+----------+
  | product_type           | int(11)     |          |
  +------------------------+-------------+----------+
  | public                 | tinyint(1)  |          |
  +------------------------+-------------+----------+
  | organization_id        | varchar(36) | FK       |
  +------------------------+-------------+----------+
  | properties             | text        |          |
  +------------------------+-------------+----------+


  **Notes:**

  The value of the product_id field is used for storing a secondary ID to
  provide additional information about the cloud, such as a hash of the cloud
  access URL.  product_id can be initialized at product creation time or later.

  The values in the "public" column are boolean numbers indicating whether the
  products are privately or publicly visible.

  Ideally, the "deleted" column should be of type tinyint(1) (which is a
  boolean in SQLAlchemy).  Int(11) is used here for being consistent with Oslo.

  The product_type column will store the pre-defined constants (enum) with
  descriptive names as defined in the OpenStack Marketplace
  ( http://www.openstack.org/marketplace/). For example: 1 = distro,
  2 = public_cloud, 3 = hosted_private_cloud, etc.

  The values in the "type" column are used by RefStack to identity the type of
  the vendor object.


REST API impact
---------------

None at the database level.


Security impact
---------------

None.

Notifications impact
--------------------

None, for the initial implementation.  In the future, RefStack may want to notify the related parties
(users or organizations) when updates are made to these tables.


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

* Create the tables.
* Create the defined methods.


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
