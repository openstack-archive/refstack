Refstack API v1
===============
This document is to serve as the complete spec for refstack's v1 api.

###Problem description#

As our requirements grow, so must the api. To maintain backwards compatibility on a live running copy of the api we have to version it to insure that older software can still have basic api functionality.

This api will be implemented at api.refstack.org. Current api functions that exist in web.py will be deprecated as software that relies on them are updated to use the new api.

###Proposed change#

This isn't so much a change as a definition of the api that has evolved so far. This way we have a v1 spec and can use it to plan for v2 features and changes.

###Alternatives#

N/A

###REST API impact#

All urls will be prefaced by */v1/* indicating version one of the api is in use.


####results#

**description:** Receive tempest test result from a remote test runner. this function expects json formated pass results.

**url:** post /v1/results

**parameters:**

str:data - a string input containing json as shown in lower example.

**post example:**

    {
     'cpid': '2fd4e1c67a2d28fced849ee1bb76e7391b93eb12',
     'duration_seconds': 23445234,
     'results': [
          {'name':'fully.qualified.test.path',
           'uid':'test uuid'}, /* if test has uid. uid has a priority */   
          {'name: 'another.test.path.without.uid'}] /* only passed tests */
    }

**normal response:** http:201 - the status has been saved

    {
      'test_run_id': '7fd4e1c67a2d28fced849ee1bb76e7391b93eb12',
    }

**failed response:** http:404 - the job_id does not exist

    {
     'message': 'the job_id does not exist.'
    }

**failed response:** http:400 - the job_id already has results

    {
     'message': 'the job_id already has results'
    }

----
**description:** Get the results of a test run in JSON format.

**url:** get /v1/results/{test_run_id}

**normal response:** http:200 - OK

    {
      'created_at': '2015-01-16 10:10:10',
      'duration_seconds': 25,
      'cpid': '6b678f2c7fa94c7e942728b300451b56',
      'results': [
           'tempest.api.test.id',
           'tempest.api.another.test.id'
       ]
    }

----

**Data model impact**

* add int field called duration_seconds to test model
* add varchar field cpid to test model
* change name of subunit field in test model to results and possibly increase length
* change name of TestStatus to Events
* add int field event_type to Events model

**Security impact**

* Does this change touch sensitive data such as tokens, keys, or user data? **no**

* Does this change alter the API in a way that may impact security, such as a new way to access sensitive information or a new way to login?  **yes**

    _we have not implemented a security model around reporting events. some discussion will need to take place to decide if this is acceptable._

* Does this change involve cryptography or hashing?  **no**

* Does this change require the use of sudo or any elevated privileges?  **no**

* Does this change involve using or parsing user-provided data? This could
  be directly at the API level or indirectly such as changes to a cache layer. **yes**

    _we will be parsing results and json data being posted to perform different actions and will therefore be vulnerable. in order to protect ourselves we will have to take care with the parsing code to ensure things are valid and not open to injection attacks_

* Can this change enable a resource exhaustion attack, such as allowing a single API interaction to consume significant server resources? Some examples of this include launching subprocesses for each connection, or entity expansion attacks in XML. **no**


**Notifications impact**

N/A

**Other end user impact**

Moving forward any changes to the testing client will need to be in sync with the api version.

**Performance Impact**

N/A

**Developer impact**

This will effect a lot of areas of existing code.. this is why the second work item below is "update exising api calls and web views so that they are compatible with the new scema" and "modify testing client to use the new api calls".

**Implementation:**

The api will be implemented as a flask application in the api.py file.

**Assignee(s)**

Primary assignee:
  dlenwell

**Work Items**

* update models to reflect above mentioned schema changes.
* update exising api calls and web views so that they are compatible with the new scema.
* replace current api.py with a new api that meets this spec.
* create validation decorator
* stand up api.refstack.org with new api.
* write api unit tests.
* modify testing client to use the new api calls.

**Dependencies**

N/A

**Testing**

* we will require api unit tests for each call and expected response.

**Documentation Impact**

* all api functions will have sphinx compatible doc tags reflecting actual usage.

**References**

N/A
