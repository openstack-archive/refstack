=======================
Refstack Specifications
=======================

This folder is used to hold design specifications for additions
to the RefStack project. Reviews of the specs are done in gerrit, using a
similar workflow to how we review and merge changes to the code itself.

The layout of this folder is as follows::

    specs/<release>/
    specs/<release>/approved
    specs/<release>/implemented

The lifecycle of a specification
--------------------------------

Specifications are proposed by adding an .rst file to the
``specs/<release>/approved`` directory and posting it for review. You can
find an example specification in ``/specs/template.rst``.

Once a specification has been fully implemented, meaning a patch has landed,
it will be moved to the ``implemented`` directory and the corresponding
blueprint will be marked as complete.

`Specifications are only approved for a single release`. If a specification
was previously approved but not implemented (or not completely implemented),
then the specification needs to be re-proposed by copying (not move) it to
the right directory for the current release.

Previously approved specifications
----------------------------------

The RefStack specs directory was re-structured during the Mitaka cycle.
Therefore, the specs approved and implemented prior to the Mitaka cycle will be
saved in the ``specs/prior/`` directories.

Others
------

Please note, Launchpad blueprints are still used for tracking the status of the
blueprints. For more information, see::

    https://wiki.openstack.org/wiki/Blueprints
    https://blueprints.launchpad.net/refstack

For more information about working with gerrit, see::

    http://docs.openstack.org/infra/manual/developers.html#development-workflow

To validate that the specification is syntactically correct (i.e. get more
confidence in the Jenkins result), please execute the following command::

    $ tox
