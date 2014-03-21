==================================
Refstack Specifications
==================================

This folder in this repo is used to hold approved design specifications for additions
to the Refstack project.  Reviews of the specs are done in gerrit, using a similar
workflow to how we review and merge changes to the code itself.

The layout of this repository is::

  specs/specification_name.rst

You can find an example spec in `/specs/template.rst`.

Specifications are proposed for a given release by adding them to the
`specs/` directory and posting it for review. The implementation
status of a blueprint for a given release can be found by looking at the
blueprint in launchpad. Not all approved blueprints will get fully implemented.

Prior to April 2014, this method was not used for spec
reviews. Prior reviews were completed entirely through Launchpad
blueprints::

  http://blueprints.launchpad.net/refstack

Please note, Launchpad blueprints are still used for tracking the
current status of blueprints. For more information, see::

  https://wiki.openstack.org/wiki/Blueprints

For more information about working with gerrit, see::

  https://wiki.openstack.org/wiki/Gerrit_Workflow

To validate that the specification is syntactically correct (i.e. get more
confidence in the Jenkins result), please execute the following command::

  $ tox
