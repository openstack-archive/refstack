=============================================
Simplify Uploads by only sending Pass results
=============================================

Blueprint: https://blueprints.launchpad.net/refstack/+spec/pass-only-uploads
Storyboard: https://storyboard.openstack.org/#!/story/108

As part of helping the community accept the publication of results, refstack
test uploads should default to only PASS results. We are NOT uploading skips
or errors. This aligns with the interop objective because we want have a
positive assertion.

Problem description
===================

Because fail results often include sensitive information it has been a pain
point for some of our early adopters to upload results to a foundation
controlled database. Since refstack really only cares about the things that
pass, we'll just parse the results and leave the fails out.

Proposed change
===============

This would involve using the subunit parsing code inside the tester. We would
run the parser on the subunit before uploading the results to the api.

We'll want to have a non-default option to send all data. Because I am sure
that some folks will want to use refstack internally for real debugging and
test regression.

If a user tries to submit results to the public api server (Regardless of what
the non-defaulting option is set to.). It will either produce an error (which I
don't think is as useful) or it will just scrub the results anyways.

Alternatives
------------

We could take the full upload and do the processing server side to accomplish
the DefCore objective; however, that does not avoid the data leak issue.

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------

This change addresses security concerns. as far as I can tell it will not
create any new ones.

Notifications impact
--------------------

It should mention that results are being scrubbed in the on screen log messages.
so that it's clear on every action.

Other end user impact
---------------------

None

Performance Impact
------------------

This will slow down the tester but not by a lot. However it will also speed up
the upload of the results since they will be trimmed.

Other deployer impact
---------------------

None

Developer impact
----------------

This could potentially be a maintance problem moving forward as we move the
subunit parsing utils into tempest then move the tester into its own repo.

It will require that someone stays on top of things durring those changes to avoid
duplication of code.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  dlenwell

Other contributors:
  catherine wrote the parsing utils. So some support might be needed.

Work Items
----------

The tester already has a stubbed out function for this code. Just needs
to be filled in.

Dependencies
============

None

Testing
=======

None

Documentation Impact
====================

It should be written down that we aren't uploading fails. So its known to
operators and they don't have to be concerned about security leaks.

But outside of that I don't see the need for documentation.


References
==========

N/A