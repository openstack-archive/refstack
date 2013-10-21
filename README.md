RefStack
========

Vendor-facing API for registration of interop-compliance endpoints and credentials for on-demand testing. 

Running at http://refstack.org
See (living) documentation at https://etherpad.openstack.org/RefStackBlueprint

http://ci.openstack.org/stackforge.html
http://ci.openstack.org/devstack-gate.html
https://github.com/openstack-infra/config/
http://pythonhosted.org/WSME/index.html


NOTES:

To install temptest so that refstack cli works to works (this will later be done with tox and in a slick way right now this is hacky) in ubuntu I did the following:

# setting up tempest fails unless I install these libs first .. for some reason pip fails if you don't. 
sudo apt-get install libxml2-dev libxslt-dev lib32z1-dev python2.7-dev libssl-dev

pip install ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.9.tar.gz


#checkout temptest
git clone git@github.com:openstack/tempest.git

cd tempest
python setup.py install




