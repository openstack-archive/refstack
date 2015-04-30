Refstack Quickstart
===================
####Install dependencies (on ubuntu 14.x)..

- `sudo apt-get install git python-dev libssl-dev python-setuptools`

- `sudo apt-get install mysql-server python-mysqldb`

- `sudo easy_install -U pip`

- `sudo easy_install -U virtualenv`

####Setup the refstack database

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

- `git clone http://github.com/stackforge/refstack`

- `cd refstack`

- Creare virtual environment: `virtualenv .venv --system-site-package`

- Source to virtual environment: `source .venv/bin/activate`


####Install Refstack application (on ubuntu 14.x)..

- `python setup.py install`

####Configuration file preparation

- Make a copy of the sample config and update it with the correct
  information of your environment. Example of config file with default
  values available in etc directory.

- At the minimum, the following values should be updated:

  - `connection` field in the `[database]`section.

    For example, if the backend database is MySQL then update:
    `#connection = <None>` to
    `connection = mysql+pymysql://refstack:<your password>@x.x.x.x/refstack`

  - `allowed_cors_origins`.

     Update to your UI server address.  For example:
    `allowed_cors_origins = http://192.168.56.104:8080`

    Note that in this example and the one below the UI and API server are
    served on the same server but on different ports.

  - `test_results_url`

   Updated to your API server address.  For example:
    `test_results_url = http://192.168.56.104:8000/output.html?test_id=%s`  

####Database sync

- Check current revision:

  `refstack-manage --config-file /path/to/refstack.conf version`

  The response will show the current database revision. If the revision is `None` (indicating a clear database), the following command should be performed to upgrade the database to the latest revision:

 - Upgrade database to latest revision:

   `refstack-manage --config-file /path/to/refstack.conf upgrade --revision head`

 - Check current revision:

   `refstack-manage --config-file /path/to/refstack.conf version`

   Now it should be `42278d6179b9`.


####Start Refstack

For the most basic setup that you can try right now, just kick off
gunicorn:

- `refstack-api --env REFSTACK_OSLO_CONFIG=/path/to/refstack.conf`

Now available:

- `http://localhost:8000/` with JSON response {'Root': 'OK'};
- `http://localhost:8000/v1/results` with response JSON including records consisted of `<test run id>`, `<upload date>` and `<cloud cpid>` of the test runs. The default response is limited to one page of the most recent uploaded test run records. The number of records per page is configurable via the Refstack configuration file. Filtering parameters such as page, start_date, end_date ... can also be used to specify the desired records. For example: get `http://localhost:8000/v1/results?page=n` will return page n of the data.

- `http://localhost:8000/v1/results/<test run id>` with response JSON including the detail test results of the specified `<test run id>`
