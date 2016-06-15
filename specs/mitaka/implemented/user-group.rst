User Group Support in RefStack
==============================

Launchpad blueprint: https://blueprints.launchpad.net/refstack/+spec/vendor-result-validation

Requirement document: https://goo.gl/bvo4FG

Data model document: https://goo.gl/zWYnoq

This spec proposes RefStack to add user group support.


Problem description
===================

As RefStack implements the vendor/product entities, RefStack needs to allow
management and visibility of these entities to a group of users not just the
user who creates the entities.


Proposed change
===============

Add the following tables to the RefStack database:

* A table named "group".
* A table named "user_to_group".

Details about these tables are described in the "Data model impact" section.

Add methods to support:

* Add a user to a group by inserting a record into the "user_to_group" table.
* Remove a user from a group

**Note:**

* Only an interop user or a user in this group can perform the action of adding a user to a group.
* Only an interop user, a user in this group, or the user himself/herself can remove a user from the group.
* In the current implementation, all users in a group are admin users with CRUD privilege.


Alternatives
------------

Alternatively, a 'role' column can be added to the user_to_group table to support
having users with different roles in a group. The various 'roles' can be
defined in a policy file.

Open to other suggestions.

Data model impact
-----------------
The following tables will be added to the RefStack database.

* "group" table

  +------------------------+-------------+----------+
  | Column                 |   Type      |          |
  +========================+=============+==========+
  | created_at             | datetime    |          |
  +------------------------+-------------+----------+
  | updated_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted                | int(11)	 |          |
  +------------------------+-------------+----------+
  | id                     | varchar(36) | PK       |
  +------------------------+-------------+----------+
  | name                   | varchar(80) |          |
  +------------------------+-------------+----------+
  | description            | text        |          |
  +------------------------+-------------+----------+

  **Note:**

  The values in the "id" column are GUIDs generated with UUID4.

* "user_to_group" table

  +------------------------+-------------+----------+
  | Column                 |   Type      |          |
  +========================+=============+==========+
  | created_at             | datetime    |          |
  +------------------------+-------------+----------+
  | updated_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted_at             | datetime    |          |
  +------------------------+-------------+----------+
  | deleted                | int(11)	 |          |
  +------------------------+-------------+----------+
  | created_by_user        | varchar(128)|          |
  +------------------------+-------------+----------+
  | _id                    | int(11)     | PK       |
  +------------------------+-------------+----------+
  | group_id               | varchar(36) | FK       |
  +------------------------+-------------+----------+
  | user_openid            | varchar(128)| FK       |
  +------------------------+-------------+----------+

  **Note:**

  Since more than one users (an interop user or a user in this group) can add
  a user to a group, the created_by_user field was added for auditing purpose.


REST API impact
---------------

None.

No REST API will be implemented in the initial phase because a group will only
be created implicitly when an organization is created.  No "group management"
features will be exposed to the end users.

Security impact
---------------

Previously private entities such as test results can only be viewed/managed by
the owner user.  The group implementation allows a group of users to
view/manage those entities.

Notifications impact
--------------------

None, for the initial implementation.  In the future, RefStack may want to
notify the related parties (users or organizations) whenever a user is added to
or removed from a group.

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

* Create database tables.
* Create the specified private methods.


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
