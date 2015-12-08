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

**Dependencies**

N/A

**Testing**

N/A

**Documentation Impact**

Cli changes should be noted in the --help output as well as written into any documentation for the tester. 

**References**

N/A

