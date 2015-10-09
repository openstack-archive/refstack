==============================================
RSA Key Existence Check for Signed Data Upload
==============================================

Launchpad blueprint:


RefStack recently added features to enable the uploading of data with key.
Currently, RefStack accepts the uploaded data regardless of whether
the public keys exist in RefStack or not. This document describes the
validation process update needed to ensure that RefStack only accepts
data with those keys that are previously imported into RefStack.


Problem description
===================

Currently, the RefStack API server would accept the uploaded data regardless
of whether the keys exist in RefStack or not. More importantly, those keys are
used to associated the test data to the users. And, there is no enforcement
that the keys used for data uploading must exist in RefStack. In addition,
for security reasons, keys are expected to be updated from time to time.
As a consequence of the non-existing or updated keys, some data will be
inaccessible.


Proposed change
===============

* RefStack API servers will check whether the key used to upload data exists in
  the 'pubkeys' table and reject the data if it does not. Note that this method
  of checking is possible because RefStack currently enforces a policy such
  that there are no duplicate public keys in the database.  This implies that
  no two users can have the same public key uploaded, key-pairs can not be
  shared, and if a user creates a new openstackid account, he/she would have to
  use a different key or delete the public key from his/her old account.

* RefStack then associate the data to the user ID of the key owner by adding,
  in the "meta" table, a "meta_key" named "user" with value being the "openid"
  from the "user" table.


Alternatives
------------

Alternatively, if RefStack wants to allow for key sharing among users in the
future, an additional user identifier parameter such as user email is needed,
besides the key, for data uploading.  In this case, RefStack will check for
for the existence of the key in the user's profile.

As for orphan data management, RefStack may want to implement a limited life
time policy for data without owner associated to them.

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
  TBD

Other contributors:
  TBD

Work Items
----------

* RefStack API server will need to validate the existing of the key in RefStack


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
