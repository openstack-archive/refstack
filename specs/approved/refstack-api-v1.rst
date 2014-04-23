===============
Refstack API v1 
===============
This document is to serve as the complete spec for refstacks v1 api. 

**Problem description**

As our requirements grow, so must the api. To maintain backwards compatibility 
on a live running copy of the api we have to version it to insure that older 
software can still have basic api functionality. 

**Proposed change**

This isn't so much a change as a definition of the api that has evolved so far. 
This way we have a v1 spec and can use it to plan for v2 features and changes. 

**Alternatives**

I am open to suggestions on better ways to maintain working older clients with 
also allowing the api to evolve. 

**Data model impact**

none.

**REST API impact**

All urls will be prefaced by */v1/* indicating version one of the api is in use. 

------------

``update-test-status``

**method:** *post*

**description:** allows remote tester to update the status of a job that was 
triggered by the api. 

**normal http response:** 201 - the status has been saved

**error http response:** 400 - either the test-id doesn't exist or the message 
was empty. 

**url:** */v1/update-test-status/*

**Parameters:**  

int:test_id - passed in the url (will take out of url)

bool:finished - boolean - indicates if job is finished yet. 

str:status - posted string

**Example:**

*curl --data "status=test complete" http://refstack.org/v1/update-test-status/100*

------------

``post-result``

**method:** *post*

**description:** Receive tempest test result from a remote test runner. this function should be able to receive raw binary subunit files as well as json formated parsed results.  The parsed results format will be useful for cloud operators who want to share results without security concerns. 

**normal http response:** 201 - the status has been saved

**error http response:** 400 - the file value wasn't posted

**url:** */v1/post-result*

**Parameters:**  

int:test_id - posted string, optional, leaving this out will write the results to the 
database as anonymous data. 

blob:file - posted string

------------

``get-miniconf``

**method:** *get*

**description:** Return a JSON of mini tempest conf to a remote test runner.

**normal http response:** 200 filename=miniconf.json

**error http response:** 400 - Invalid test ID

**url:** */v1/get-miniconf*

**Parameters:**  

int:test_id - tells refstack which cloud to grab extra config options for. 

------------

**API methods to be deprecated** 

`* no methods will be removed until they are no longer needed.`

get-script - this will no longer be needed if we package and version the test executer. 

get-testcases - this will no longer be needed because the tester will just run all the tests.. period. 

**Security impact**

* Does this change touch sensitive data such as tokens, keys, or user data? **no**

* Does this change alter the API in a way that may impact security, such as
  a new way to access sensitive information or a new way to login?  **no**

* Does this change involve cryptography or hashing?  **no**

* Does this change require the use of sudo or any elevated privileges?  **no**

* Does this change involve using or parsing user-provided data? This could
  be directly at the API level or indirectly such as changes to a cache layer. **maybe 
  the accept results method could use some tightening up**

* Can this change enable a resource exhaustion attack, such as allowing a
  single API interaction to consume significant server resources? Some examples
  of this include launching subprocesses for each connection, or entity
  expansion attacks in XML. **no**


**Notifications impact**

N/A

**Other end user impact**

Moving forward any changes to the testing client will need to be in sync with
the api version. 

**Performance Impact**

N/A

**Developer impact**

This will change the way the current docket templated tester installs the 
testing script. currently it pulls the script from an api call then runs 
it.. thats a nightmare security risk.. we can't leave the functionality so 
removing that method from the api v1 spec should address that. 

**Implementation:**

**Assignee(s)**

Primary assignee:
  dlenwell

**Work Items**

* remove get-script method
* organize all pure api calls into a different file.
* add code to import the api functions when web.py is loaded. 
* update the existing api to have the correct HTTP response
* add timeout and error reporting to update_status method

**Dependencies**

N/A

**Testing**

Since we currently have no tests this isn't an issue.. although perhaps we 
should write tests for our own stuff.. since you know testing is at the core 
of refstack. 

**Documentation Impact**

Since we have not written docs for the api.. let this document serve as the 
starting place for that.

**References**

N/A
