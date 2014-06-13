#!/usr/bin/env python
#
# Copyright (c) 2014 OpenStack Foundation, All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# This file creates and runs Tempest in a Docker Container

FROM ubuntu:13.10
MAINTAINER OpenStack RefStack Project

RUN apt-get update

# Install git, python and essential tools
RUN apt-get install -y git python-setuptools curl ftp
RUN easy_install pip

# Install dependencies (small bites are easier to troubleshoot)
RUN apt-get install -y libxml2-dev libxslt-dev lib32z1-dev 
RUN apt-get install -y python2.7-dev python-dev libssl-dev
RUN apt-get install -y python-libxml2 libxslt1-dev libsasl2-dev
RUN apt-get install -y libsqlite3-dev libldap2-dev libffi-dev

# Setup Environment by Cloning refstack & tempest (choose right branch)
RUN mkdir temp
RUN git clone https://github.com/stackforge/refstack.git
RUN git clone https://github.com/openstack/tempest.git 

# Version of TCUP 
# Changing REBUILDs the container from this point forward
ENV TCUP 0.1.0

# Using refstack & tempest dependencies
RUN pip install -r /refstack/requirements.txt
RUN pip install -r /refstack/test-requirements.txt

# Running tempest setup
RUN cd tempest && git checkout stable/havana
RUN cd tempest && python setup.py install

# The tcup.py frontend must be used to run this Docker image
# The following CMD statement will run and print the documentation
# to inform the user of the proper way of running tcup. This
# CMD statement is overriden by tcup.py
CMD cat refstack/doc/tcup.md
