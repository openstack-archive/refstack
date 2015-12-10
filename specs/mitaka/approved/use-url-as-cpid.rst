=============================================
Use Cloud URL as the Cloud Provider ID (CPID)
=============================================

Launchpad blueprint:

This spec proposes RefStack to add a method to use the cloud
access URL as the base to generate the CPID.


Problem description
===================

As defined in the "Test Submission API should use Target Identity
Endpoint UUID" specification (refstack-org-api-cloud-uuid.rst).  Currently,
RefStack uses the cloud's Identity (Keystone) UUID as the CPID.

For Keystone V2 API, this ID can be the ID of any one of the
three access endpoints, namely admin, public or private endpoints. However,
for Keystone V3 API, this ID is the ID of the Keystone service. Furthermore,
when testing a distro product, the Identity ID will be different every time
a cloud is stood up, regardless that whether this cloud is built by the
same person, with exactly the same OpenStack code and configuration. In such
circumstances, multiple CPIDs could represent a single cloud.

We have also encountered some cases that the cloud's Keystone does not even
returns the identity service ID in the tokens it returns. In addition, there
is recent request for RefStack to support uploading test results that were
not collected using refstack-client.  These type of data in subunit format
won't have CPID created at testing time.  RefStack should provide a method
to generate CPID without the need of re-connecting to the cloud again.


Proposed change
===============

In addition to the current practice of using the different types of Identity
ID for CPID, RefStack should add additional support to generate the
CPID based on the cloud URL. This will also be used as the failover method
for CPID.


Alternatives
------------

For consistency, RefStack should consider to only use the cloud access URL
to generate the UUID for CPID. In consequence, RefStack no longer has to keep
track and adjust to changes in Keystone client and API for retrieving the
the CPID.

Open to other suggestions.


Data model impact
-----------------

None.

There is no data modal change needed.


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

With this failover addition, refstack-client should never again fail due to
CPID retrieval error. This also allows RefStack to provide users with an
option to upload data in subunit format.


Performance Impact
------------------

None

Other deployer impact
---------------------

There is possibility of CPIDs being the same for two different clouds.
This can happen primarily in the private address space, where people may
have use the same IP address such as 192.168.*.* (or whatever commonly used
default addresses) for keystone address. Since this likely won't be the case
with actual production clouds and it is a last resort, we are okay with this
possibility.

Furthermore, RefStack is no longer completely dependent on whether or not
the cloud's Keystone even returns the Identity service ID in the tokens it
returns.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  TBD

Other contributors:
  TBD

Work Items
----------

* Develop code to generate CPID based on access URL


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
