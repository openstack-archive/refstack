Base TCUP environment for refstack.org
==========================================
https://blueprints.launchpad.net/refstack/+spec/standalone-tcup-driver

TCUP (Tempest in a Container, Upload from Probe) is a self-contained, universal Tempest environment that can be widely used by the community with minimal effort AND minimal support effort by the Refstack team.

Problem description
===================

For DefCore and the core definition, we need to collect lots and lots of test runs against deployed OpenStack clouds.  Many of these clouds are behind firewalls and not accessible by 3rd parties.  So we need to make it super easy to make running Tempest and result uploads as accessible as possible.

Community access is the goal of TCUP.  While the original and primary intent of Tempest was to test OpenStack code, having a large body of tests creates unique opportunities for us.  DefCore uses the tests as a way to define core capabilities.

Installing and configuring Tempest presents a challenge for many in the community.  TCUP's job is to reduce that complexity to the smallest possible set.

Who are "Users" below?  The user in this context is the TCUP user, not user inferred from the OpenStack API credentials.

Requirements:

* It should not matter which Linux distro they are using
* Users should not have to figure out which Refstack and Tempest code to check out (beyond the single tcup.py file)
* Users should not have to deal with packages or pips (beyond Docker and the minimal tcup requirements)
* Users should not have to determine where to upload their results (but could override)
* Users identities must be hidden unless they agree/ask to have them published.  There is a risk that their OpenStack credentials may be revealed in log messages - this should be addressed.
* When the test is complete, the test system dissolves

Anti-Requirements:

* Users should not need to checkout or clone any code
* Users should not have to edit configuration files

.. image:: https://wiki.openstack.org/w/images/f/f4/Tcup_flow.png
   :width: 700px
   :alt: TCUP workflow

Proposed change
===============

TCUP should be designed in as simple a way as possible.

Running TCUP should only require Docker (.9+), a single tcup.py file with minimal dependencies, working OpenStack cloud credentials and an Internet connection for install and results upload.  The cloud being tested does _not_ have to be public.  TCUP will work as long as the user and the TCUP install has network access to the cloud being tested.

Environment variables from the host (OS_*) will be passed into the container.  The container should not start unless critical OS_ variables are in place.  The specific OS_ items are limited:

  * OS_AUTH_URL
  * OS_TENANT_NAME
  * OS_USERNAME
  * OS_PASSWORD

There should be a `--debug` mode to allow for user testing and debug.  The debug flag should NOT start tests automatically and should map the user pwd into /dev in the TCUP container.

There must be both a way to use local code (refstack) to run TCUP and also a simple file download approach.  These methods should be functionally identical.

While there may be broad uses of TCUP for test automation, it is not desirable to overload them at the expense of manual usability.  TCUP should be kept very simple for users in this pass.

By default, TCUP will upload results to the Refstack site (this is a requirement above); however, we anticipate other use cases.  For users who do not want to upload their results, they can change their API target parameters.  This will allow users to instead upload their results to an internal Refstack site or simply save the results to their local drive.

Alternatives
------------

* THESE ARE INCLUDED FOR COMPLETENESS, NOT IMPLEMENTATION *

It would be possible to create a single-use VM for this testing.  That would require much more download time, build effort and maintenance.

An additional method is to package execute_test on its own allowing it to install on fedora and ubuntu.  It already has tempest havana stable as a dependancy.  It can be installed and the rc file can be sourced and it can be kicked off.  No container would be needed and  you can log into any cloud instance on any cloud provider that has network reach to the cloud you want to test. Start an ephemeral vm and log into it and run two commands.

Yet another approach is to assume tempest havana is already installed.  Users can invokes execute_test directly without using docker or any container.  This omits the "minimal setup" TCUP approach.

It would be possible to setup a cloud-based process to run Tempest (this is a Refstack use case); however, this would not reach private clouds.  It also does not give the user control of the data.

Data model impact
-----------------

None.

REST API impact
---------------

None; however, TCUP will rely on a stable upload REST API.


Security impact
---------------

User passwords are passed into the container and should be redacted from log entries or error messages.

We should prompt the user (from the tcup.py) code to enter a password if none is provided in the environment.

Passwords must not be stored by TCUP!


Notifications impact
--------------------

None

Other end user impact
---------------------

TCUP is designed as a stand-alone capability.  It should not have interactions with other parts of the system except via the API as noted above.

Performance Impact
------------------

None.

Other deployer impact
---------------------

The community version of TCUP does NOT have to be coupled to other test running models.

It is _not_ desirable to complicate TCUP to serve other uses.

Developer impact
----------------

None.  TCUP should use the standard API.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  robhirschfeld

Other contributors:
  praveen (test)
  alexhirschfeld (dev & test)
  dlenwell (review)
  rockyg (documentation) * these documents are ripe with raw material for docs :)

Work Items
----------

* build TCUP docker container (via Dockerfile)
* build tcup.py to build and launch docker
* document run process
* update configuration generator to use environment variables
* integrate execute_test scripts into TCUP
* integrate default upload target into TCUP

Dependencies
============

* execute_test scripts must support environment variables
* upload API must function correctly

Testing
=======

Manual environment testing by Refstack and community.

Documentation Impact
====================

TCUP needs detailed community facing documentation and video tours.

References
==========

* http://docker.io