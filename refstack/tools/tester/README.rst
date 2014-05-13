Execute Test
============

Execute test is a command line utility that allows you to execute tempest runs with generated configs. When finished running tempest it sends the raw subunit data back to an api. 

**Usage** 

First make sure you have some stuff installed

`apt-get update`


`apt-get install -y git python-pip`

`apt-get install -y libxml2-dev libxslt-dev lib32z1-dev python2.7-dev libssl-dev libxml2-python`

`apt-get install -y python-dev libxslt1-dev libsasl2-dev libsqlite3-dev libldap2-dev libffi-dev`

`pip install --upgrade pip>=1.4`
`pip install virtualenv`

Then you'll need to setup the tempest env.. from the refstack dir.

`cd refstack/tools/execute_test/`

the following command installs stable havana tempest in a virtual env named 'test_runner'. putting tempest in `./test_runner/src/tempest`

`./setup_env`

From here you have two options..

a. if you are triggering this test from the web gui you can use the `/get-miniconf` method ..

i.e. `./execute_test --url refstack.org --test-id 235 --tempest-dir ./test_runner/src/tempest --conf-json {section:{option:value}}`

or

b. my recomendation which is to source an openstack rc file you download from the cloud you want to test.

i.e.

`source openstackrc.sh`

`./execute_test --env --url refstack.org --test-id 235 --tempest-dir ./test_runner/src/tempest`

