TCUP Configuration
===========================

The following instructions are designs run Refstack/Tempest in a container with minimal setup on your system.

> These steps are _not_ do not install Refstack for contributions or development, they are intended for a user who wants to just run and report test results.

1. Make sure you have python and wget installed for your operating system.

1. Install Docker using [[https://www.docker.io/gettingstarted/#h_installation]]
  1. Note: if you are in an environment with a proxy, make sure you configure `/etc/default/docker` to leverage the proxy too!
  1. You may want to prep-the environment using 

1. Get the code: `wget https://raw.githubusercontent.com/stackforge/refstack/master/scripts/tcup.py`
  1. note: you can also get the code by cloning the Refstack and running the code in `/scripts/tcup.py`

1. Set your environment variables to access the test target cloud
  1. generally, you will `source openrc.sh` to load the cloud credentials and URLs

1. Run TCUP: `sudo python tcup.py`
  1. if you want to work on the code from Refstack, use `sudo python scripts/tcup.py'


## Trouble Shooting TCUP

There are several ways to trouble shoot, TCUP. 

1. Enter your docker container using `run -i -t [image id from tcup.py] /bin/bash `
1. Check your environment variables include the OS_* values using `export`
1. Make sure you can access Keystone using `curl $OS_AUTH_URL`
1. Make sure your credentials are working using `keystone catalog`
1. `Export DEBUG=true` to turn on additional logging and force TCUP into manual run mode

## Docker Tips 
1. You can run Docker without sudo!
  1.  `sudo usermod -a -G docker <your-user>` (to permanently run Docker
  without sudo)
  1. you will need to reboot after this change (but you can wait until we tell you to reboot later)
  1. if you don't want this to be permanent or active before the reboot use, `sudo chmod 666 /var/run/docker.sock`

1. You can inspect which containers are running!
  1. `sudo docker ps` shows the running containers
  1. `sudo docker attach` allows you to connect to a container (may have to press enter)
  1. exit from inside the container with `Ctrl-p` + `Ctrl-q`
1. Orphaned Containers: Over time, you may end up with [orphaned contaniers](http://jimhoskins.com/2013/07/27/remove-untagged-docker-images.html), use the following to clean them up
  1. `sudo docker rm $(docker ps -a -q)`
  1. `sudo docker rmi $(docker images | grep "^<none>" | awk "{print $3}")`

## For Developers

If you run TCUP in debug mode (`export DEBUG=true`) then TCUP will automatically mount your PWD as /dev.
If you run TCUP from your Refstack clone, then you can work directly in Refstack code from inside
a TCUP container from the /dev directory.