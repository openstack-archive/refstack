How to upload test results to RefStack
======================================

RefStack allows test results contributors to submit test results and have them
displayed either anonymously, or identified with a vendor. As such, test
results should be uploaded with validated users. Users will first log into
RefStack with their OpenStack ID to upload their public keys. RefStack test
results can then be uploaded to RefStack using the corresponding private key.
By default, the uploaded data isn't shared, but authorized users can decide to
share the results with the community anonymously.

The following is a quick guide outlining the steps needed to upload your first
set of test results.

####Register an OpenStack ID

The RefStack server uses OpenStack OpenID for user authentication. Therefore,
the RefStack server requires that anyone who wants to upload test data to have
an OpenStack ID. As you click on the Sign In/Sign Up link on the RefStack
pages, you will be redirected to the official OpenStack user log in page where
you can either log in with your OpenStack ID or register for one. The
registration page can also be found directly through:
[https://www.openstack.org/join/register](https://www.openstack.org/join/register).

####Generate ssh keys locally

You will need to generate ssh keys locally. If your operating system is a Linux
distro, then you can use the following instructions.

First check for existing keys with command:

- `ls -al ~/.ssh`

If you see you already have existing public and private keys that you want to
use, you can skip this step; otherwise:

- `ssh-keygen -t rsa -b 4096 -C "youropenstackid"`

The 'youropenstackid' string is the username you chose when you registered for
your OpenStack ID account. Enter the file name in which to save the key
(/home/you/.ssh/id_rsa), then press enter. You will be asked to enter a
passphrase. Just press enter again as passphrase protected keys currently
aren't supported. Your ssh keys will then be generated.

####Sign Key with RefStack Client

** IMPORTANT ** You must have the RefStack client on you computer to complete
this step.

Generate a signature for your public key using your private key with
[refstack-client](https://github.com/openstack/refstack-client)

- `./refstack-client sign /path-of-sshkey-folder/key-file-name`

The '/path-of-sshkey-folder' string is the path of the folder where the
generated ssh keys are stored locally. The 'key-file-name' portion refers to
the private key file name. If the command runs correctly, there will be output
like below:

    Public key:
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDSGo2xNDcII1ZaM3H2uKh3iXBzvKIOa5W/5HxKF23yrzwho7nR7td0kgFtZ/4fe0zmkkUuKdUhOACCD3QVyi1N5wIhKAYN1fGt0/305jk7VJ+yYhUPlvo...

    Self signature:
    19c28fc07e3fbe1085578bd6db2f1f75611dcd2ced068a2195bbca60ae98af7e27faa5b6968c3c5aef58b3fa91bae3df3...

####Upload the ssh public key and the signature

Sign into [https://refstack.openstack.org](https://refstack.openstack.org) with
your OpenStack ID. Click the "Profile" link in the upper right corner. Now
click the "Import public key" button on your profile page. A popup window with
two entry fields will appear. Just copy and paste the key and signature
generated in the previous step into the corresponding textboxes.  

Note that the literal strings 'Public key:' and 'Self signature:' from the refstack-client "sign" command output should not be copied/pasted into the text boxes. Otherwise you will get an error like:

- `Bad Request Request doesnt correspond to schema`

 Once complete, click the 'Import public key' button.

####Upload the test result with refstack-client

- `./refstack-client upload /path_to_testresult_json_file  --url https://refstack.openstack.org/api -i  ~/.ssh/id_rsa`

** NOTE ** Users may need to add the '--insecure' optional agrument to the command string if certificate validation issues occur when uploading test result. To use with insecure:

- `./refstack-client upload --insecure /path_to_testresult_json_file  --url https://refstack.openstack.org/api -i  ~/.ssh/id_rsa`

The `path_to_testresult_json_file` here is the json file of your test result.  
By default, it's in `.tempest/.testrespository/<test-run-number>.json` where refstack-client runs from.  
Here '<test-run-number>' is a serial number that matches its corresponding subunit file name.  

If the command runs correctly, there will be output like below:

    Test results will be uploaded to https://refstack.openstack.org/api. Ok? (yes/y): y
    Test results uploaded!
    URL: https://refstack.openstack.org/#/results/88a1e6f4-707d-4627-b658-b14b7e6ba70d.

You can find your uploaded test results by clicking the 'My Results' link on
the RefStack website.
