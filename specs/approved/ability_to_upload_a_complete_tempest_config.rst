===========================================
Ability to upload a complete tempest config
===========================================

storyboard: https://storyboard.openstack.org/#!/story/105

**Problem description**

It makes sense that if an admin already has a working and tested tempest config,
they should be able to use it with the refstack tester.

**Proposed change**

Allowing the user to use a custom tempest config would require changes to the
tester cli as well as the web interface. We can safely break the code commits
for this into two tasks. 

* The CLI would require an extra argument for a path to a config file. As well
as some logic that bypassed the internal config generation.

* The Web UI will need some re-working to allow for this.

Wireframes will be added to this spec before any ux is implemented on the front end.

* web ui should be simple and clear.
* user should select a radio button indicating wether the tester should attempt to
generate a tempest config or upload a working on.
* uploaded tempest files shouldn't be written to disk. rather they should be
packaged into the workload for triggering the test run.

**Alternatives**

None off hand.

**Data model impact**

None.

**REST API impact**

None

**Performance Impact**

This should speed up the tester because now it will not have to
generate/discover config or prepare the cloud to match config options.

**Developer impact**

n/a

**Implementation:**

**Assignee(s)**

Primary assignee:
  dlenwell

**Work Items**

* Implement CLI code
* add hook for skipping config generation
* design wireframes for ux changes and add to spec.
* Update TCUP to enable this feature.

**Dependencies**

N/A

**Testing**

N/A

**Documentation Impact**

Cli changes should be noted in the --help output as well as written into any documentation for the tester. 

**References**

N/A

