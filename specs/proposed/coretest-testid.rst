
=================================================
Use fully qualified test id in the coretests file
=================================================

Launchpad blueprint:


This document describes the format for the test ids that will be used in the
DefCore coretests.json file.


Problem description
===================

The coretests.json file includes a list of tests that are defined as "core" by
the DefCore committee.  Currently, the coretests.json file (in the
defcore/havana directory) uses the method names defined in the Tempest Python
test classes as the test names.  While these method names are unique in Havana,
it is not the case in Icehouse where some of the method names are being used by
multiple test classes of different OpenStack components.


Proposed change
===============

The proposal is to adopt the test id as used by the subunit package to identify
each individual test. The test id is a fully qualified name which includes the
fully qualified class name of the Python test class and the method name. Using
this test id format will also help the performance of processing subunit test
results against the core tests list for compliance checking.

The following is an example which shows how the test_get_default_quotas test is
currently defined in the coretests.json file versus the proposed test id format.

* Current definition

 .. parsed-literal::
  "test_access_public_container_object_without_using_creds":\
   { "file": "test_object_services.py" }

* Proposed test id format

 .. parsed-literal::
  "tempest.api.object_storage.test_object_services.PublicObjectTest.\
  test_access_public_container_object_without_using_creds"


Alternatives
------------

Open to suggestions on better ways to uniquely identify each test case with run
time processing performance in mind.


Data model impact
-----------------

None


REST API impact
---------------

None


Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

Using the test id will help the performance of run time result processing.


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
  Catherine Diep

Other contributors:
  Rob Hirschfeld

Work Items
----------

* Catherine to create the corresponding test id from the tests listed in the
  coretests.json file.
* Rob Hirschfeld to review and validate the result test id list


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
