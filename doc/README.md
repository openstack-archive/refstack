RefStack Documentation
=============================

Welcome to RefStack.  This project helps OpenStack collect and distribute test and validation information.

Executing Tests
-----------------------------

The heart of RefStack is running tests.  We've done a lot of things to make that easier (like [T-CUP](tcup.my)), but here's the basic things you need to do to run Tempest in RefStack:

1. Setup a system with all the Operating System dependencies
1. Clone Refstack and Tempest (get the branch you want)
1. Install and pip dependencies from the requirements files
1. Run the Tempest setup.py install