======================================
separate refstack tester from refstack
======================================

**Problem description**

The refstack tester needs to be easily installable on its own without checking
out the refstack code.

**Proposed change**

This would require taking the code that lives in refstack/tools/tester and moving
it into its own repository. probably in openstack-infra.

**Alternatives**

we could leave the code were it is and force anything that wants to install it to
checkout the whole of refstack to do so.

**Data model impact**

none.

**REST API impact**

none.

**Security impact**

* Does this change touch sensitive data such as tokens, keys, or user data? **no**

* Does this change alter the API in a way that may impact security, such as
  a new way to access sensitive information or a new way to login?  **no**

* Does this change involve cryptography or hashing?  **no**

* Does this change require the use of sudo or any elevated privileges?  **no**

* Does this change involve using or parsing user-provided data? This could
  be directly at the API level or indirectly such as changes to a cache layer. **no**

* Can this change enable a resource exhaustion attack,  such as allowing a
  single API interaction to consume significant server resources? Some examples
  of this include launching subprocesses for each connection, or entity
  expansion attacks in XML. **no**

**Notifications impact**

none.

**Other end user impact**

The tester would need to remain compatible with the v1 api spec.

**Performance Impact**

none/

**Developer impact**

When finished tcup would need to have the tester as a dependancy.

**Implementation:**

**Assignee(s)**

Primary assignee:
  dlenwell

**Work Items**

* put code from refstack/tools/tester in external github repo (i.e. github.com/dlenwell/refstack-tester)
* add basic unit and node test to new project to insure it works in ci
* create project in openstack-infra/config for project with the above repo set as its upstream.
* insure that project has the enable storyboard flag.
* add refstack-tester to requirements.txt in refstack (will still be needed by tcup)
* deprecate code in refstack/tools/tester

**Dependencies**

none.

**Testing**

The new project will require a base set of tests so that ci works propperly.

**Documentation Impact**

Since we have not written docs for the api.. let this document serve as the
starting place for that.

**References**

N/A
