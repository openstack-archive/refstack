==================================
Refstack Specifications
==================================

This folder is used to hold design specifications for additions
to the Refstack project. Reviews of the specs are done in gerrit, using a similar
workflow to how we review and merge changes to the code itself.

Specifications are proposed by adding an .rst file to the `specs/proposed` directory and posting it for review. Not all approved blueprints will get fully implemented. You can find an example spec in `/specs/template.rst`.

When a spec has passed the review process and discussions in our weekly meetings it will 
be moved to 'specs/approved/'. At that time the blueprint will be marked as approved and assigned to someone.

Once a spec has been fully implemented, meaning a patch has landed that references the blueprint, it will be moved again to 'specs/completed'.

Prior to April 2014, this method was not used for spec
reviews. Prior reviews were completed entirely through Launchpad
blueprints::

  http://blueprints.launchpad.net/refstack

Please note, Launchpad blueprints are still used for tracking the
current status of blueprints. For more information, see::

  https://wiki.openstack.org/wiki/Blueprints

For more information about working with gerrit, see::

  http://docs.openstack.org/infra/manual/developers.html#development-workflow

To validate that the specification is syntactically correct (i.e. get more
confidence in the Jenkins result), please execute the following command::

  $ tox
