==================================
DefCore Managed Files
==================================

This folder contains DefCore committee managed files that provide trusted guidance for the OpenStack community.

Assets for each release are tracked in dedicated subdirectories so JSON schema may change per release if needed.

NOTE: Changes to files in these subdirectories requires approval of the Defcore committee chair(s).

----------------------------------
Havana Release
----------------------------------

## coretests.json

Contains the list of tests that are considered must-pass for the Havana Core.

## capabilities.json

Contains a grouping map between Capabilities and tests.  This file should contain all tests, not just the core ones.

## drivers.json

Contains the list of OpenStack drivers and their qualified status.

NOTE: Changes to the drivers list requires involvement of the parties impacted by that change via +1 vote.