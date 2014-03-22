TCUP Configuration
===========================

  # Install Docker using [[https://www.docker.io/gettingstarted/#h_installation]]

  # Get the code
  git clone http://github.com/stackforge/refstack

  # enter RefStack
  cd refstack

  # create/copy your OpenStack credentials into openrc.sh an file

  # Create the TCUP container
  docker build t-container

  # Run the container
  docker run -v `pwd`:/tcup:rw -i -t 32fe2d733d51 /bin/bash

  # Inside the container run the following
  source tcup/openrc.sh
  tcup/run_in_tcup.py
