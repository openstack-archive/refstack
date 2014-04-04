Using Execute Test 
======================================

Used to run Tempest from Refstack: `refstack/tools/execute_test.py`

Command Line
--------------------------------------

* tempest-home: path to tempest, e.g. /tempest
* callback: url to post results formatted as ${api_addr} ${test_id}"

Environment Variables
--------------------------------------

Instead of a configuration file, you can also start Execute_Test using environment variables.

Required:
* OS_AUTH_URL : Keystone URL
* OS_REGION_NAME : Region
* OS_USERNAME : Username
* OS_PASSWORD : Password (passed in clear, do not save into file!)
* OS_TENANT_NAME : Tenant name or ID

Optional:
* test_id : System Generated, may be overridden
* api_addr
* TEMPEST_IMAGE_REF: name of image used for testing.  Defaults to "cirus"