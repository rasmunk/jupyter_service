import os

c = get_config()
pwd = os.path.dirname(__file__)

c.JupyterHub.spawner_class = 'mig.SwarmSpawner'
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'

c.JupyterHub.base_url = '/dag'

c.JupyterHub.cleanup_servers = True
c.JupyterHub.debug = True

# First pulls can be really slow, so let's give it a big timeout
c.SwarmSpawner.start_timeout = 60 * 15

c.SwarmSpawner.jupyterhub_service_name = 'nbi-jupyter-service-devel_jupyterhub'

c.SwarmSpawner.networks = ["nbi-jupyter-service-devel_default"]

notebook_dir = os.environ.get('NOTEBOOK_DIR') or '/home/jovyan/work/'
c.SwarmSpawner.notebook_dir = notebook_dir

mounts = [{'type': 'volume',
           'driver_config': 'rasmunk/sshfs:latest',
           'driver_options': {'sshcmd': '{sshcmd}', 'id_rsa': '{id_rsa}',
                              'allow_other': '', 'big_writes': ''},
           'source': 'sshvolume-user-{username}',
           'target': notebook_dir
           }]

# 'args' is the command to run inside the service
c.SwarmSpawner.container_spec = {
    'args': ['/usr/local/bin/start-singleuser.sh', '--NotebookApp.ip=0.0.0.0',
             '--NotebookApp.port=8888',
             '--NotebookApp.allow_origin=http://dag000.science'],
    'env': {'JUPYTER_ENABLE_LAB': '1',
            'TZ': 'Europe/Copenhagen'}
}

# Before the user can select which image to spawn,
# user_options has to be enabled
c.SwarmSpawner.use_user_options = True

# Available docker images the user can spawn
c.SwarmSpawner.dockerimages = [
    {'image': 'nielsbohr/base-notebook:devel',
     'name': 'Image with automatic {replace_me} mount, supports Py2/3 and R',
     'mounts': mounts},
    {'image': 'nielsbohr/base-notebook:devel',
     'name': 'Basic Python Notebook'}
]

# Authenticator -> remote user header
c.JupyterHub.authenticator_class = 'jhub_remote_auth_mount.MountRemoteUserAuthenticator'

# Service that checks for inactive notebooks
# Defaults to kill services that hasen't been used for 2 hours
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': 'python cull_idle_servers.py --timeout=7200'.split(),
    }
]

# Limit cpu/mem to 4 cores/8 GB mem
# During conjestion, kill random internal processes to limit
# available load to 1 core/ 2GB mem
c.SwarmSpawner.resource_spec = {
    'cpu_limit': int(8 * 1e9),
    'mem_limit': int(8192 * 1e6),
    'cpu_reservation': int(1 * 1e9),
    'mem_reservation': int(1024 * 1e6),
}
