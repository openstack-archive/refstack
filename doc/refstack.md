Refstack Quickstart
===================
To run refstack for development or to have a gui for running tests behind your firewall.

Git you clonin'

`git clone http://github.com/stackforge/refstack`

`cd refstack`

Install dependencies (on ubuntu 13.x)..

`apt-get install python-dev`

`apt-get install python-pip`

`easy_install -U setuptools`

`python setup.py install`

`pip install -r test-requirements.txt`

Update the "app_address" parameter in the config.json file to the correct address of your refstack server.

Setup or update the database

`cd refstack/db/migrations`

NOTE: you are going to have to modify the db connection string in `alembic.ini` to get this working

PROTIP: if you just want to test this out, use `-n alembic_sqlite` to make a local sqlite db

`alembic -n alembic_sqlite upgrade head`
or
`alembic upgrade head` If you've got mysql or another database of choice.

Plug this bad boy into your server infrastructure.
We use nginx and gunicorn, you may use something else if you so desire.

For the most basic setup that you can try right now, just kick off
gunicorn:

`gunicorn_pecan refstack/api/config.py`

Now available http://localhost:8000/ with JSON response {'Root': 'OK'}
and http://localhost:8000/v1/results/ with JSON response {'Results': 'OK'}.
