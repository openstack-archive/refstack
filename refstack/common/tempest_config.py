
class TempestConf(dict):
    """temptest config options. gets converted to a tempest config file"""
    def __init__(self):
        """ sets up the default configs"""
        self['DEFAULT'] = {
            'debug':True,
            'use_stderr':False,
            'log_file':'',
            'lock_path':'',
            'default_log_levels':"""tempest.stress=INFO,amqplib=WARN,
                sqlalchemy=WARN,boto=WARN,suds=INFO,keystone=INFO,
                eventlet.wsgi.server=WARN"""}

        self['identity'] = {
            'catalog_type': 'identity',
            'disable_ssl_certificate_validation': False,
            'uri': '',
            'uri_v3': '',
            'region': 'RegionOne',
            'username': '',
            'password': '',
            'tenant_name': '',
            'alt_username': '',
            'alt_password': '',
            'alt_tenant_name': '',
            'admin_username': '',
            'admin_password': '',
            'admin_tenant_name': '',
            'admin_role': ''}


        self['compute'] = {
            'catalog_type': 'compute',
            'allow_tenant_isolation': True,
            'allow_tenant_reuse': True,
            'image_ref': '',
            'image_ref_alt': '',
            'flavor_ref': '',
            'flavor_ref_alt': '',
            'image_ssh_user': '',
            'image_ssh_password': '',
            'image_alt_ssh_user': '',
            'image_alt_ssh_password': '',
            'build_interval': '',
            'build_timeout': '',
            'run_ssh': False,
            'ssh_user': '',
            'fixed_network_name': '',
            'network_for_ssh': '',
            'ip_version_for_ssh': '',
            'ping_timeout': '',
            'ssh_timeout': '',
            'ready_wait': 0,
            'ssh_channel_timeout': 60,
            'use_floatingip_for_ssh': True,
            'create_image_enabled': True,
            'resize_available': True,
            'change_password_available': False,
            'live_migration_available': False,
            'use_block_migration_for_live_migration': False,
            'block_migrate_supports_cinder_iscsi': False,
            'disk_config_enabled': True,
            'flavor_extra_enabled': True,
            'volume_device_name': ''}

        self['compute-admin'] = {
            'username': '',
            'password': '',
            'tenant_name': ''}

        self['image'] = {
            'catalog_type': 'image',
            'api_version': 1,
            'http_image': ''}

        self['network'] = {
            'catalog_type': 'network',
            'api_version': '2.0',
            'tenant_network_cidr': '10.100.0.0/16',
            'tenant_network_mask_bits': 28,
            'tenant_networks_reachable': False,
            'public_network_id': '',
            'public_router_id': ''}

        self['volume'] = {
            'catalog_type': 'volume',
            'disk_format': 'raw',
            'build_interval': 1,
            'build_timeout': 400,
            'multi_backend_enabled': False,
            'backend1_name': 'BACKEND_1',
            'backend2_name': 'BACKEND_2',
            'storage_protocol': 'iSCSI',
            'vendor_name': 'Open Source'}
        
        self['object-storage'] = {
            'catalog_type': 'object-store',
            'container_sync_timeout': 120,
            'container_sync_interval': 5,
            'accounts_quotas_available': True,
            'operator_role': 'Member'}

        self['boto'] = {
            'ssh_user': 'cirros',
            'ec2_url': 'http://172.16.200.130:8773/services/Cloud',
            's3_url': 'http://172.16.200.130:3333',
            'aws_access': '',
            'aws_secret': '',
            's3_materials_path': '',
            'ari_manifest': 'cirros-0.3.1-x86_64-initrd.manifest.xml',
            'ami_manifest': 'cirros-0.3.1-x86_64-blank.img.manifest.xml',
            'aki_manifest': 'cirros-0.3.1-x86_64-vmlinuz.manifest.xml',
            'instance_type': 'm1.nano',
            'http_socket_timeout': 30,
            'num_retries': 1,
            'build_timeout': 400,
            'build_interval': 1}

        self['orchestration'] = {
            'catalog_type': 'orchestration',
            'build_interval': 1,
            'build_timeout': 300,
            'instance_type': 'm1.micro',
            '#image_ref': 'ubuntu-vm-heat-cfntools',
            '#keypair_name': 'heat_key'}

        self['dashboard'] = {
            'dashboard_url = http://172.16.200.130/',
            'login_url = http://172.16.200.130/auth/login/',

        self['scenario'] = {
            'img_dir': '',
            'ami_img_file': 'cirros-0.3.1-x86_64-blank.img',
            'ari_img_file': 'cirros-0.3.1-x86_64-initrd',
            'aki_img_file': 'cirros-0.3.1-x86_64-vmlinuz',
            'ssh_user': 'cirros',
            'large_ops_number': '0',

        self['cli'] = {
            'enabled': True,
            'cli_dir': '/usr/local/bin',
            'timeout': 15 }

        self['service_available'] = {
            'cinder': True,
            'neutron': False,
            'glance': True,
            'swift': False,
            'nova': True,
            'heat': False,
            'horizon': True}

        self['stress'] = {
            'max_instances': 32,
            'log_check_interval': 60,
            'default_thread_number_per_action': 4 }
