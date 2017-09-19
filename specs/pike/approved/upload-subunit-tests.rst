=============================================
Upload Subunit Data From Test Results
=============================================

Launchpad blueprint:

* https://blueprints.launchpad.net/refstack/+spec/subunit-data-upload

This specification describes an expansion of the RefStack API's
functionality to allow for upload of the subunit data which corresponds
to a given set of test results.

Problem description
===================

Currently, all test results uploaded to the RefStack website consists
of a json file containing only the portion of the RefStack run pertaining
to the passed tests. This limitation dates back to the the start of the
RefStack project. At that time, Defcore (which is now known as interop-WG)
was very concerned about the possibility that private data may be included
in the subunit upload file. Defcore was concerned that vendors might, for
that reason, be hesitant to upload data into RefStack for fear of
unintentionally revealing vendor-specific data such as reasons for test
failures.  For this reason, Defcore agreed unanimously that RefStack should
care only about passing tests, and not failed or skipped ones.

The risk, with this resolution, however, is that not including a full set of
results means that it would be fairly simple to falsify those results in
order to make an OpenStack instance appear to be more interoperable than
it actually is. This too, was discussed at the time, and Defcore eventually
arrived at the conclusion that, in the end, it would be better to accept
vendor results in good faith, but to always leave the door open for users
and Foundation staff to verify those results independently. This decision
did not, however, account for the possibility that vendors seeking support
during the process of verifying the interoperability of their product may
need a way to securely share subunit data for review by Foundation staff.

Proposed change
===============

In order to move towards having a more reliable and verifiable collection
of RefStack results, we intend to add functionality to the RefStack
toolkit that will allow for the upload of the subunit data related to a given
set of test results. This data would be private, only accessible to the party
uploading it, and to foundation staff, to be used for result integrity
verification as well as debugging assistance. Upload of subunit data will not,
for the time being, be required.

After discussing a number of data storage methods at the 7/18/17 RefStack
meeting[3], we settled upon saving the newly usable subunit data in the
current database. With a small adjustment to our alembic settings (which
will keep the version tables from colliding), this could be done using the
existing subunit2sql toolkit[4]. In order to apply the table name change,
we will build in a series of functions that check refstack.conf and rename
the existing alembic version table if needed. This added functionality,
when merged and functional, will make RefStack one of only two OpenStack
projects (according to oslo.conf docs[7])that is currently capable of
modifying configuration at runtime without a service restart. The usage of
subunit2sql will do a lot of the heavy lifting for us, as far as data import
goes, as well as keeping the storage method of test data consistent across
the board.

For the time being, we plan to link the subunit data will be linked to the
corresponding test results via a key value pair in the metadata table that
is an existing part of the RefStack database.

Toolset to use:

subunit2sql

Alternatives
------------

Though we did eventually decide upon storing the new data in a new, separate
database, a few alternate options were discussed during the 7/18/17 RefStack
meeting[3]. The alternate options discussed were:
* Save subunit files as-is in a file system. This has the benefit of being the
  least processing-intensive option for saving the data, as it would literally
  just save the output into a file. It may, however, make subunit data upload
  a bit less elegant, as well as being a deviation from the way test run data
  is managed throughout the rest of RefStack.
* Save subunit data in the RefStack database and tables by building in the
  functionality required to save and manage it. Like the option listed above,
  this option keeps test run data stored consistently across refstack, which
  would make the changes to the API more consistent as well. It would also
  avoid the overhead that would result from using a separate database, as well
  as any redundancies that resulted from using a second, separate database.
  However, any redundancy would be fairly minor due to the extremely limited
  scope of the data we are currently storing from each test run, and this would
  leave more of the implementation up to us, which, because of how well
  subunit2sql's schema fulfills the needs of this change, may be wholly
  unnecessary.
* Save subunit data in a separate database created by subunit2sql. This has the
  benefit of having all of the functionality we need without forcing us to
  reinvent the wheel, but it also carries with it the overhead of having to use
  a second database. This option doesn't make much sense, however, given that
  we can actually use subunit2sql's toolkit in the current refstack database,
  as long as we can configure the database to use an extra (differently named)
  alembic version table for refstack's core db.

Data model impact
-----------------

We may be able to use the tables created by subunit2sql within the RefStack
database. These tables (for reference) are mapped out below:::

 --------------------------------------
 |               tests                |
 --------------------------------------
 |   id           |  String(256)      |
 |   test_id      |  String(256)      |
 |   run_count    |  Integer          |
 |   failure      |  Integer          |
 |   run_time     |  Float            |
 --------------------------------------

 ----------------------------------------
 |              runs                    |
 ----------------------------------------
 |  id            |  BigInteger         |
 |  skips         |  Integer            |
 |  fails         |  Integer            |
 |  passes        |  Integer            |
 |  run_time      |  Float              |
 |  artifacts     |  Text               |
 |  run_at        |  DateTime           |
 ----------------------------------------

 ---------------------------------------------------
 |                    test_runs                    |
 ---------------------------------------------------
 |  id                      |  BigInteger          |
 |  test_id                 |  BigInteger          |
 |  run_id                  |  BigInteger          |
 |  status                  |  String(256)         |
 |  start_time              |  DateTime            |
 |  start_time_microseconds |  Integer             |
 |  stop_time               |  DateTime            |
 |  stop_time_microseconds  |  Integer             |
 |  test                    |  Test                |
 |  run                     |  Run                 |
 ---------------------------------------------------

 -------------------------------------------
 |            run_metadata                 |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  run_id        |  BigInteger            |
 |  run           |  Run                   |
 -------------------------------------------

 -------------------------------------------
 |          test_run_metadata              |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  test_run_id   |  BigInteger            |
 |  test_run      |  TestRun               |
 -------------------------------------------

 -------------------------------------------
 |            test_metadata                |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  key           |  String(255)           |
 |  value         |  String(255)           |
 |  test_id       |  BigInteger            |
 |  test          |  Test                  |
 -------------------------------------------

 -------------------------------------------
 |            attachments                  |
 -------------------------------------------
 |  id            |  BigInteger            |
 |  test_run_id   |  BigInteger            |
 |  label         |  String(255)           |
 |  attachment    |  LargeBinary           |
 |  test_run      |  TestRun               |
 -------------------------------------------

more details about this data model can be found in the source docs for
subunit2sql[5]

If we end up being unable to integrate the two databases into one at this time,
we plan to use the metadata table which already exists in the RefStack internal
db to store a key pair that links the existing test data to the newly added
subunit data.

REST API impact
---------------

We will need to implement a new REST API for the  upload of subunit data
from the client, and then use subunit2sql to process and save the data
into the database.


Security impact
---------------
It has been suggested that uploading the subunit data for tests may expose
private data. However, it was determined in the 6/27/2017 RefStack meeting[1]
that if any such data is revealed through this upload, it would be due to a
leak in tempest's logging procedures, not the upload of this new type of data.

This was also discussed at the 6/28/17 Interop-wg meeting[2]. It was at this
meeting that was confirmed that we would implement this change using an
opt-in flag, so that those who are still concerned about the security of
uploading the results do not, by default, have to upload their data. It was
also determined that, due to the fact that this design reflects a fairly
significant reversal in a past decision, that the community should be
properly notified. This decision also resulted in the following action plan:
1. write an email to distribute to the mailing list
2. send out the official decision after the email is distributed
3. change the official interop docs to reflect this change

Another concern was that a database injection attack may be possible, if an
attacker were to use maliciously crafted subunit data. This threat, also,
does not appear to be much of a danger, as the mass majority of the data
written to the database is done after the subunit data is processed, meaning
that there are very few places in which raw strings are written into the db.
We need to look a little  more into whether sql does enough input sanitization
for our needs.

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance impact
-------------------

None

Other deployer impact
---------------------

We will also need to adjust refstack-client to be able to consume the new API
feature while uploading subunit data.

One of the most user-visible part of this change would be the creation of a
flag option which enables the upload of the subunit data to the refstack site,
which would modify the existing procedure in that we would need to build in
functionality that would allow for the additional data upload.

We would also need to add a second flag to the database sync functionality in
order to allow for the alternate naming of the alembic version table, which
enables us to use both subunit2sql and refstack tables and functionality
within the same database.

Developer impact
----------------

None

Implementation
==============

Assignees(s)
------------

Primary assignee:
  Megan Guiney

Other contributors:
  Paul Van Eck (subunit data upload ui in refstack-client)

Work Items
----------
* Add a CONF option to allow for the usage of nonstandard alembic
  version table names.
* Add a utility that allows for the runtime checking and alteration
  of alembic version table names.
* Create an API at the server side to accept the subunit data
* At the server side, use subunit2sql to process the subunit data
* Link subunit data to existing set of refstack results.
* Create UI to upload subunit data (completed, as of 1/20/2016[6],
  though may require update)
* Create a UI to display subunit data. There may already be one, but
  we need to make sure such a utility exists. We also need to decide
  whether the results should be viewable via the refstack website.



Dependencies
============

Testing
=======

Documentation Impact
====================

We will need to update the docs to reflect the additions to the API, the
database, and to refstack-client as well.

References
==========
[1] http://eavesdrop.openstack.org/meetings/refstack/2017/refstack.
    2017-06-27-19.00.log.html
[2] http://eavesdrop.openstack.org/meetings/interopwg/2017/interopwg.
    2017-06-28-16.00.log.html
[3] http://eavesdrop.openstack.org/meetings/refstack/2017/refstack.
    2017-07-18-19.00.log.html
[4] https://git.openstack.org/cgit/openstack-infra/subunit2sql
[5] https://docs.openstack.org/subunit2sql/latest/data_model.html
[6] https://review.openstack.org/#/c/265394/
[7] https://docs.openstack.org/oslo.config/latest/configuration/
    mutable.html
