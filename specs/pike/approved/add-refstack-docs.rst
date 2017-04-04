=============================================
Displaying RefStack Documentation Directly on Website
=============================================

Launchpad blueprint:

* https://blueprints.launchpad.net/refstack/+spec/user-documentation

This specification defines the changes to the "About" page of the RefStack
website in that are neccessary in order to allow RefStack documentation to be
displayed natively on the RefStack site.

Problem description
===================

To make RefStack information more accessible to users, RefStack documentation
should be displayed in a format more closely matching that of the rest of
the RefStack site. Currently, documentation is maintained as RST files in the
‘doc’ folder of the RefStack repository, but with this change, users will also
be able to view them as HTML files via the RefStack site.


Proposed change
===============

As mentioned above, it would be ideal to be able to access RefStack
documentation in HTML format. The current plan is to use docutills in
combination with sphinx in order to create HTML templates which will then
be able to be integrated into the existing RefStack website.

Another goal of this documentation update will be to a duplicate set of docs
intended for users from the rest of the docs, in order to ensure that they
will be more easily accessed by end users. These docs will be displayed on the
the RefStack website. A second set of docs, the RefStack Project docs,
will be hosted at the OpenStack docs website. These will be the same docs
that are published in the RefStack repo in RST format.


Possible libraries to use:

sphinx

docutils

Alternatives
------------

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

Other contributors:
  Luz Cazares

Work Items
----------

None

Dependencies
============

None

Testing
=======

None

Documentation Impact
====================

User specific documents will now be available on the RefStack website in
simple HTML format. It will be listed under the "About" section on the main
menu bar. This will be a change from the current state in that users will now
be able to view documentation concerning running tests and uploading results
in a format which is similar to the rest of the RefStack website.

RefStack documentation will now also be available on the main OpenStack docs
site. These docs will use the same source as those hosted on the RefStack site.

References
==========

