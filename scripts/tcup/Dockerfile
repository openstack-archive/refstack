
FROM ubuntu 
RUN apt-get update

# Downloading git

RUN apt-get install -y git python-setuptools

RUN easy_install pip

#Downloading dependencies
RUN apt-get install -y libxml2-dev libxslt-dev lib32z1-dev python2.7-dev libssl-dev

#other dependencies
RUN apt-get install -y python-dev libxslt1-dev libsasl2-dev libsqlite3-dev libldap2-dev libffi-dev ftp
# RUN pip install ftplib
RUN pip install http://gd.tuwien.ac.at/pub/libxml/python/libxml2-python-2.6.9.tar.gz
# http://gd.tuwien.ac.at/pub/libxml/python/libxml2-python-2.4.16.tar.gz
# RUN pip install ftplib libxml2-python

# Cloning keystone? 


# Cloning tempest

RUN git clone https://github.com/openstack/tempest

#running setup
RUN cd tempest && python setup.py install

#making file to add exterior files

RUN mkdir temp

#Tempest config creator
ADD https://raw.github.com/dlenwell/refstack/master/refstack/common/tempest_config.py /temp/

#MORE DEPENDENCIES (for tempest config builder)
ADD https://raw.github.com/openstack/keystone/master/requirements.txt /temp/
ADD https://raw.github.com/openstack/keystone/master/test-requirements.txt /temp/

#using dependencies
RUN pip install -r /temp/requirements.txt
RUN pip install -r /temp/test-requirements.txt

#Running tempest config creator


#Publishing to refstack
#ADD <url> /temp/

#rest of file

