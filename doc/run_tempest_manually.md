Below Instructions guide you to run tempest manually from tcup container :

Pre-requisites : set up docker container by following instructions in the tcup.md document
Once you are in TCUP container, make sure you can able to ping $OS_AUTH_URL

Instructions :

1)cd tempest/etc

2)copy tempest.conf.sample tempest.conf

3)update the tempest.conf file with the target cloud values(AUTH_URL,User name,Password,Tenent name,Tenent Id,IMAGE_ID,IMAGE_ID_ALT)


4)update below attributes in tempest.conf  with the OS_VALUES then save the tempest.conf file

**Tempest.conf**                      ** Replace with ****
uri   =                                 OS_AUTH_URL
username  =                             OS_USERNAME
password  =                             OS_PASSWORD
tenant name  =                          OS_TENANT_NAME
image_ref   =                           {$IMAGE_ID}(run glance image-list command on target cloud,
                                                                 copy image id then replace here)
image_ref_alt  =                        {$IMAGE_ID_ALT}(run glance image-list command on target
                                                           cloud,copy image id then replace here)
5)cd tempest

6)nosetests -v tempest ( to run full tempest suits)

If you want to stop the tempest execution at the first failure,use below command

7)nosetests -vx tempest
