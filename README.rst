refstack
========

**What is refstack?**

- Toolset for testing interoperability between OpenStack clouds.
- Database backed website supporting collection and publication of
  Community Test results for OpenStack.
- User interface to display individual test run results.

**Overview**


refstack intends on being THE source of tools for interoperability testing
of OpenStack clouds.

refstack provides users in the OpenStack community with a Tempest wrapper,
refstack-client, that helps to verify interoperability of their cloud
with other OpenStack clouds. It does so by validating any cloud
implementation against the OpenStack Tempest API tests.

**refstack and DefCore** - The prototypical use case for refstack provides
the DefCore Committee the tools for vendors and other users to run API
tests against their clouds to provide the DefCore committee with a reliable
overview of what APIs and capabilities are being used in the marketplace.
This will help to guide the DefCore-defined capabilities and help ensure
interoperability across the entire OpenStack ecosystem. It can also
be used to validate clouds against existing DefCore capability lists,
giving you assurance that your cloud faithfully implements OpenStack
standards.

**Value Add for Vendors** - Vendors can use refstack to demonstrate that
their distros, and/or their customers' installed clouds remain with OpenStack
after their software has been incorporated into the distro or cloud.

**refstack consists of two parts:**

* **refstack-api**
   Our API isn't just for us to collect data from private and public cloud
   vendors. It can be used by vendors in house to compare interoperability
   data over time.

   * API and UI install docs: `doc/refstack.md <doc/refstack.md>`_
   * repository: http://git.openstack.org/cgit/stackforge/refstack
   * storyboard: https://storyboard.openstack.org/#!/project/700
   * reviews: https://review.openstack.org/#q,status:open+refstack,n,z

* **refstack-client**
   refstack-client contains the tools you will need to run the DefCore tests.

   * repository: http://git.openstack.org/cgit/stackforge/refstack-client
   * storyboard: https://storyboard.openstack.org/#!/project/703
   * reviews: https://review.openstack.org/#q,status:open+refstack-client,n,z

**Get involved!**

* Mailing List: fits@OpenStack.org
* IRC: #refstack on Freenode
* Dev Meetings: Mondays @ 19:00 UTC in #openstack-meeting-alt on Freenode
* Web-site: http://refstack.net
* Wiki: https://wiki.OpenStack.org/wiki/RefStack
