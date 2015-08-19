Run-in-docker manual
===================

The main purpose of the `run-in-docker` script is to provide a convenient way
to create a local setup of RefStack inside a Docker container. It should be
helpful for new developers and also for testing new features.

####Requirements:
- `Docker >= 1.6` (How to update on [Ubuntu](http://www.ubuntuupdates.org/ppa/docker))

####How to use:
Just run the `run-in-docker` script, but is important to first set env[REFSTACK_HOST]
with the public host/IP for your local API. If you want to test RefStack with OpenStackid
you should point a valid local alias here. For example:

`export REFSTACK_HOST=myrefstack.com`

By default 127.0.0.1 is used.

After it completes, check that the site is running on https://127.0.0.1.

The script will build a RefStack docker image with all dependencies, and will run
a container from this image. By default, RefStack will run inside this container.
You also can run `run-in-docker bash` to get access into the container. If you stop
the RefStack server by pressing 'Ctrl-C', the container is kept alive and will be
re-used next time.

You can customize the RefStack API config by editing `docker/templates/refstack.conf.tmpl`.
It is a bash template, so you can use ${SOME\_ENV\_VARIABLE} in it.

This script can make the reviewing process much easier because it creates separate
containers for each review. Containers get names in the form refstack_{REVIEW-TOPIC}.
Database schema changes are automatically handled, too, where the script creates a data
container for each database revision (refstack\_data\_{DATA-BASE-REVISON}) and reuses it
where possible. For example, if a new review uses an existing database revision, that
database container will be used.

####Available script options:
- `-r`    Force delete the RefStack container and run it again.
          This will update the RefStack config from template noted above.
- `-i`    Run a container with isolated MySQL data. By default MySQL data is stored in
          a refstack\_data\_{DATA-BASE-REVISON} container. It reuses this container if such
          one exists. If you want to drop the DB data, just execute
          `sudo docker rm refstack_data_{DATA-BASE-REVISON}`.
- `-b`    Force delete RefStack image and build it again. This rebuids the Python and JS
          environment for RefStack.
- `-d`    Turn on debug information.
- `-h`    Print usage message.

####Useful in-container commands/aliases:
- `api-up` - sync project and run the RefStack API
- `api-init-db` - initialize the RefStack database
- `api-db-version` - get current migration version of the RefStack database
- `api-sync` - sync project files in the container with the project files on the host
- `activate` - activate the python virtual env
- `mysql` - open the MySQL console
