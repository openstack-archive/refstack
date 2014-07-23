
==========================
Identify code to deprecate
==========================

Storyboard: https://storyboard.openstack.org/#!/story/110

This spec identifies code that should be deprecated.

Problem description
===================

At the Juno summit, we have learned of many other groups working on
things that overlap with refstack. In addition, there are new
requirements and changes in refstack that may also result in the
refactoring of refstack code. This spec identifies code that should
either be deprecated or moved into other projects.

In addition to that. We've decided to simplify the design of refstack by
removing both the "official" and local testing tracks from refstack.

Instead we will allow vendors/operators to run tests on their own and
simply submit the results using the refstack-client.


Proposed change
===============

* Remove templated config config creation:

  Until auto configuration exists in tempest. refstack has decided to
  remove support for in app generated config. Instead we will allow
  operators to use their own known config file with the refstack-client.

  This change would require:

  *  Removing the tempest.conf file generation code in refstack-client.
     Add option in refstack-client to take a tempest.conf file as input
     parameter. It is the caller's responsibility to construct the
     tempest.conf file and pass it to refstack-client.

  * Several functions in web.py will be removed.

    * get_testcases
    * get_miniconf
    * get_script

  When/if a common tool to generate tempest.conf becomes available we
  may revisit reintroducing this feature.

  There is currently a blueprint under review
  (https://review.openstack.org/#/c/94473/) to build a tool that will
  generate proper tempest.conf using as few input arguments as possible.

* Remove code to trigger test from web ui functionality.

  Because we've removed the use cases for both local and official web
  driven test runs. We can remove all the excess web ui for creating new
  clouds and starting and monitoring test runs.

* tools/tempest_tester.py

  This code being replaced by the new refstack-client.

* tools/tempest_subunit_test_result.py

  refstack is no longer parsing any raw subunit. The refstack-client
  only uploads an array of passing tests.

  We originally planned to contribute this code to the tempest project.
  However the tempest ptl is not interested in it because they'd prefer
  folks just use the built in subunit parsers.

  We have additionally thought of moving this code into refstack-client.
  I am not sure that is the correct path. However I am open to
  discussion.

* tools/execute_test

  Being replaced by the new refstack-client.

  Also need to remove the following files:

  1: refstack/tools/:
     docker_buildfile.py,
     docker_buildfile.template
  2: refstack/templates/
     show_report.html,
     show_status.html,
     tempest.conf,
     test_cloud.html

Data model impact
-----------------

None, The database will remain as it is.


REST API impact
---------------

Many functions which are currently included in the web.py file will be
removed once the new v1 api lands.


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

None

Other deployer impact
---------------------

None

Developer impact
----------------

None


Implementation
==============

Details in the Work Items section.

Assignee(s)
-----------

Primary assignee:
  Catherine Diep

Other contributors:
  IBM team member

Work Items
----------

Use the "Proposed Change" section to populate work items.


Dependencies
============

refstack-client and v1 api landing.


Testing
=======

None


Documentation Impact
====================

None


References
==========

* Tempest blueprint for tempest.conf creation

  https://review.openstack.org/#/c/94473/
