==========================================
Test Submission API should use Target Identity Endpoint UUID
==========================================

story: "Use keystone uuid with cloud id"
ref: https://storyboard.openstack.org/#!/story/135


In order to ensure that multiple test runs are attributed to the same cloud,
test runner needs to use a consistent, discoverable and unique identifier
for each cloud test.  This allows multiple users to correlate results from
the same cloud.

Problem description
===================

Refstack is designed to have minimal user security and configuration overhead;
consequently, there are no mechanisms in the short term to ensure that a user's 
test results are authorized (see note).  To create valid results, refstack needs a way to 
know when multiple runs are against the same targets so that comparisons are valid.

  > Note: In the future, Refstack will include user authentication.  At that point
  it will be possible to associate uploaded data to users and vendors in an 
  authoritative way.

To solve this problem, refstack needs a unique handle for each cloud tested
that is unique and also discoverable to the test runner.

Some requirements:

* No round trips to refstack before a test is submitted (do not pre-create cloud)
* Minimal trust of users (do not require user credentials for uploads)
* Users should not be expected to remember cloud IDs
* Multiple users of same cloud should be tracked together

Proposed change
===============

When test runner submits results, it should submit with the Identity Endpoint
UUID (aka Keystone end point under serviceCatalog/service["identity"]/endpoint[?id]).

The refstack API should accept EITHER the user's created refstack cloud ID or the
discovered Endpoint UUID.  If the refstack cloud ID is passed and no cloud
exists then refstack should create a new refstack cloud.

Alternatives
------------

Refstack could use a different endpoint for the ID

Refstack could stop using its own cloud ID and only use endpoint IDs

Possible addition: we may want to also track the cloud endpoint URL.  This
could be a possible added field for the JSON upload.  While this will
help identify clouds, it could also reveal more information than the
user wants disclosed.  We should only implement this with user permission.

Data model impact
-----------------

We have to add the endpoint ID as a field into the Cloud model.

REST API impact
---------------

The Test Upload API needs to be modified to accept either the Test ID or the
endpoint UUID.  If the endpoint UUID is not in the URL then it should be included
in the JSON payload.

Security impact
---------------

Improvement: this helps reduce the need of passing refstack authentication to ensure
that cloud results are linked to individual clouds or users.


Notifications impact
--------------------

None.

Other end user impact
---------------------

Users will not have to pre-create clouds before using
refstack.

Users will have to be able to assign clouds to endpoint UUIDs.

Performance Impact
------------------

Should improve performance because round trips on result
uploads are avoided.

Other deployer impact
---------------------

None.

Developer impact
----------------

Should simplify developer work.

Implementation
==============

Assignee(s)
-----------

TBD

Work Items
----------

* determine forumula for endpoint UUID (if any needed)
* get and add cloud epid to results upload
* add cloud epid to model
* update api to response correctly for epid lookup

Dependencies
============

API v1 spec.

Testing
=======

We need to validate the endpoint IDs correctly resolve to clouds.

Documentation Impact
====================

We should explain how clouds are identified in the documentation so that
users will understand the impact of re-installing and how to keep results
together even if the cloud changes.

We will also have to explain how to associate results to a user managed
cloud.

References
==========

https://storyboard.openstack.org/#!/story/135
