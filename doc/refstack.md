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

- At the minimum the value of the `connection` field in the `[database]`
  section should be updated. For example, if the backend database is MySQL
  then update: `#connection = <None>` to
  `connection = mysql://refstack:<your password>@x.x.x.x/refstack`

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

Now available http://localhost:8000/ with JSON response {'Root': 'OK'}
and http://localhost:8000/v1/results/ with JSON response {'Results': 'OK'}.
