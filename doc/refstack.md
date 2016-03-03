RefStack Quickstart
===================

You can use docker for [one-click setup](run_in_docker.md)
or follow step-by-step instructions below.

####Install API dependencies (on ubuntu 14.x)..

- `sudo apt-get install git python-dev libssl-dev python-setuptools`

- `sudo apt-get install mysql-server python-mysqldb`

- `sudo easy_install -U pip`

- `sudo easy_install -U virtualenv`

####Install RefStack UI dependencies

- `curl -sL https://deb.nodesource.com/setup | sudo bash -`

- `sudo apt-get install nodejs`

####Setup the RefStack database

- Log into MySQL: `mysql -u root -p`

- After authentication, create the database:

  `CREATE DATABASE refstack;`

- Create a refstack user:

  `CREATE USER 'refstack'@'localhost' IDENTIFIED BY '<your password>';`

  or using hash value for your password

  `CREATE USER 'refstack'@'localhost'
   IDENTIFIED BY PASSWORD '<hash value of your password';`

- Grant privileges:

  `GRANT ALL PRIVILEGES ON refstack . * TO 'refstack'@'localhost';`

- Reload privileges:

  `FLUSH PRIVILEGES;`

- Exit MySQL: `quit`

####Git you clonin'

- `git clone http://github.com/openstack/refstack`

- `cd refstack`

- Create virtual environment: `virtualenv .venv --system-site-package`

- Source to virtual environment: `source .venv/bin/activate`

####Install RefStack application (on ubuntu 14.x)..

- `pip install .`

####Install needed RefStack UI library dependencies

- `npm install`

####API configuration file preparation

- Make a copy of the sample config file (etc/refstack.conf.sample) and
  update it with the correct information of your environment. Examples
  of the config parameters with default values are included in the
  sample config file.

- You should ensure that the following values in the config file are noted and
  properly set:

  - `connection` field in the `[database]`section.

    For example, if the backend database is MySQL then update:
    `#connection = <None>` to
    `connection = mysql+pymysql://refstack:<your password>@x.x.x.x/refstack`

  - `ui_url` field in the `[DEFAULT]` section.

    This should be the URL that the UI can be accessed from. This will likely
    be in the form `http://<your server IP>:8000` (8000 being the default port
    RefStack is hosted on). For example: `http://192.168.56.101:8000`

  - `api_url` field in the `[api]` section.

    This should be the URL that the API can be accessed from. This, in most
    cases, will be the same as the value for `ui_url` above.

  - `app_dev_mode` field in the `[api]` section.

    Set this field to true if you aren't creating a production-level RefStack
    deployment and are just trying things out or developing. Setting this field
    to true will allow you to quickly bring up both the API and UI together,
    with the UI files being served by a simple file server that comes with
    Pecan.

####Create UI config file

From the RefStack project root directory, create a config.json file
and specify your API endpoint inside this file. This will be something like
{"refstackApiUrl": "http://192.168.56.101:8000/v1"}:

- `cp refstack-ui/app/config.json.sample refstack-ui/app/config.json`

####Openstack OpenID endpoint configuration (optional)

If you are only interested in the uploading and viewing of result sets, then
this section can be ignored. However, in order for user accounts and
authentication to work, you need to make sure you are properly configured
with an OpenStack OpenID endpoint. There are two options:

* Use the official endpoint [openstackid.org](https://openstackid.org)
* Host your own openstackid endpoint

Since openstackid checks for valid top-level domains, in both options you will
likely have to edit the hosts file of the system where your web-browser for
viewing the RefStack site resides. On Linux systems, you would modify
`/etc/hosts`, adding a line like the following:

  `<RefStack server IP>  <some valid domain name>`

  Example:

  `192.168.56.101  myrefstack.com`

On Windows, you would do the same in `%SystemRoot%\System32\drivers\etc\hosts`.
Alternatively, you can add a custom DNS record with the domain name mapping
if possible.

Note that doing this requires you to modify the config.json file and the
`api_url` and `ui_url` fields in refstack.conf to use this domain name instead
of the IP.

**Option 1 - Use Official Endpoint**

Using the official site is probably the easiest option as no additional
configuration is needed besides the hosts file modifications as noted above.
RefStack, by default, points to this endpoint.

**Option 2 - Use Local Endpoint**

Instructions for setting this up are outside of the scope of this doc, but you
can get started at [https://github.com/openstack-infra/openstackid]
(https://github.com/openstack-infra/openstackid)
or [https://github.com/fremontlabs/vagrant-openstackid]
(https://github.com/fremontlabs/vagrant-openstackid).
You would then need to modify the `openstack_openid_endpoint` field in the
`[osid]` section in refstack.conf to match the local endpoint.

####Database sync

- Check current revision:

  `refstack-manage --config-file /path/to/refstack.conf version`

  The response will show the current database revision. If the revision is
  `None` (indicating a clear database), the following command should be
  performed to upgrade the database to the latest revision:

 - Upgrade database to latest revision:

   `refstack-manage --config-file /path/to/refstack.conf upgrade --revision head`

 - Check current revision:

   `refstack-manage --config-file /path/to/refstack.conf version`

    Now it should be some revision number other than `None`.


####Start RefStack

A simple way to start refstack is to just kick off gunicorn using the
`refstack-api` executable:

- `refstack-api --env REFSTACK_OSLO_CONFIG=/path/to/refstack.conf`

If `app_dev_mode` is set to true, this will launch both the UI and API.

Now available:

- `http://<your server IP>:8000/v1/results` with response JSON including
  records consisting of `<test run id>` and `<upload date>` of the test runs.
  The default response is limited to one page of the most recent uploaded test
  run records. The number of records per page is configurable via the RefStack
  configuration file. Filtering parameters such as page, start_date, and
  end_date can also be used to specify the desired records. For example:
  GET `http://<your server IP>:8000/v1/results?page=n` will return page *n*
  of the data.

- `http://<your server IP>:8000/v1/results/<test run id>` with response JSON
  including the detail test results of the specified `<test run id>`

####(Optional) Configure Foundation organization and group

Overall RefStack admin access is given to users belonging to a "Foundation"
organization. To become a Foundation admin, first a "Foundation" organization
must be created. Note that you must have logged into RefStack at least once so
that a user record for your account is created.

- Log into MySQL: `mysql -u root -p`

- Create a group for the "Foundation" organization:

  `INSERT INTO refstack.group (id, name, created_at) VALUES (UUID(), 'Foundation Group', NOW());`

- Get the group ID for the group you just created:

  `SELECT id from refstack.group WHERE name = 'Foundation Group';`

- Get your OpenID:

  `SELECT openid from refstack.user WHERE email = '<your email>';`

- Add your user account to the previously created "Foundation" group. Replace
  `<Group ID>` and `<Your OpenID>` with the values retrieved in the two previous steps:

  `INSERT INTO refstack.user_to_group (created_by_user, user_openid, group_id, created_at)
   VALUES ('<Your OpenID>', '<Your OpenID>', '<Group ID>', NOW());`

- Create the actual "Foundation" organization using this group:

  `INSERT INTO refstack.organization (id, type, name, group_id, created_by_user, created_at)
   VALUES (UUID(), 0, 'Foundation', '<Group ID>', '<Your OpenID>', NOW());`
