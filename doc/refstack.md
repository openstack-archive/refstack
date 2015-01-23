Refstack Quickstart
===================

Instruction to run refstack for development or behind your firewall.

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

- Update the db connection strings in following files to the correct
 information of your environment.

 - The `sqlalchemy.url = mysql://root:passw0rd@127.0.0.1/refstack` string
   in the `./refstack/db/migrations/alembic.ini` file.

 - The `'db_url': 'mysql://root:passw0rd@127.0.0.1/refstack'` string in the
   `./refstack/api/config.py` file.

 - NOTE: You may need to also update the `'debug': False` string in the
   `./refstack/api/config.py` file for development.

- Creare virtual environment: `virtualenv .venv --system-site-package`

- Source to virtual environment: `source .venv/bin/activate`

- Install refstack: `python setup.py install`

- Create tables in the refstack database.

 - `cd ./refstack/db/migrations/`

 - `alembic upgrade head`

 - `cd ../../..`

Plug this bad boy into your server infrastructure.

We use nginx and gunicorn, you may use something else if you so desire.

For the most basic setup that you can try right now, just kick off
gunicorn:

`gunicorn_pecan --debug refstack/api/config.py`

Now available http://localhost:8000/ with JSON response {'Root': 'OK'}
and http://localhost:8000/v1/results/ with JSON response {'Results': 'OK'}.