Gearman based test queue for refstack.org
==========================================

launchpad blueprint:
https://blueprints.launchpad.net/refstack/+spec/refstack-org-gearman-tester

Set up gearman worker/client for triggering official test runs from refstack.org
Some notes about using this template:

* build gearman client / job monitor

* stand alone worker script that does not need refstack installed.

Problem description
===================

In an effort to make this hostable long term scalable we need a way to manage a queue of tests that run on a distributed infrastructure. For that I like gearman.

This covers the Public cloud vendor official testing use case.

.. image:: https://wiki.openstack.org/w/images/1/16/Refstack-publiccloud-usecase.png
   :width: 700px
   :alt: Public Cloud official test channel use case


Proposed change
===============

This spec covers the following deliverables;

 *  gearman client side code. (https://review.openstack.org/#/c/84270/)
 *  gearman worker code (wip)
 *  api method for reporting failure

Alternatives
------------

There are a lot of other job queue type things .. I happen to love gearman and the infra team has a gearman based system in place already.. they know how to trouble shoot it and tweak it for performance.

Data model impact
-----------------

This uses the current models without any changes.

REST API impact
---------------

* new method.. report_failure
  * this method will accept failure report form running remote tests

  * Method type: POST

  * if result is accepted responds with 202

  * Expected error http response code(s)

    * 400 bad requst.. payload was missing?

    * 405 not authorized, this method should only allow failure reports from known gearman hosts

  * URL: /response/failure

  * Parameters

    * payload - the payload object that was passed into the worker to begin with

    * test_id - the test id

Security impact
---------------

* Does this change touch sensitive data such as tokens, keys, or user data? NO

* Does this change alter the API in a way that may impact security, such as
  a new way to access sensitive information or a new way to login? NO

* Does this change involve cryptography or hashing? NO

* Does this change require the use of sudo or any elevated privileges? NO

* Does this change involve using or parsing user-provided data? This could
  be directly at the API level or indirectly such as changes to a cache layer. YES

* Can this change enable a resource exhaustion attack, such as allowing a
  single API interaction to consume significant server resources? Some examples
  of this include launching subprocesses for each connection, or entity
  expansion attacks in XML.  NO (thats why we use gearman)

Notifications impact
--------------------

None

Other end user impact
---------------------

Aside from the API, are there other ways a user will interact with this feature?

NO

Performance Impact
------------------

The idea behind using gearman for this is that we can scale the worker pool in and out
depending on demand. So there is no real need to worry about performance impacts.


Other deployer impact
---------------------

* using the gearman testing option will require two settings in `refstack.cfg` GEARMAN_SERVER and GEARMAN_PORT will need to be set with the location and port of the gearmand server. 

* This change will require being enabled in the same file with the TEST_METHOD value set to "gearman". 

Developer impact
----------------

none

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  dlenwell

Other contributors:
  rockyg (documentation)

Work Items
----------

* gearman client side code. (https://review.openstack.org/#/c/84270/)
* gearman worker code (wip)
* report failure api call

Dependencies
============

extends openstack-infra/gear
   https://github.com/openstack-infra/gear

will also require a running gearmand service someplace accessible to both worker and client.

Testing
=======

TBD

Documentation Impact
====================

This should already be included in the high level architecture documentation for refstack.

References
==========

* http://gearman.org
