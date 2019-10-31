from io import StringIO
from time import sleep
from typing import Optional

import digitalocean
from django.conf import settings
from fabric import Connection


class DigitalOceanError(Exception):
    pass


class DigitalOceanProvider:
    tag = "minecraftserver"
    region = "nyc1"
    image = "debian-9-x64"
    size = "s-2vcpu-4gb"

    poll_interval = 5
    timeout = 600

    def __init__(self, config, token: Optional[str] = None):
        self._token = token if token else settings.DIGITALOCEAN_TOKEN
        self.config = config

    def get_ssh_keys(self):
        """
        Get all keys registered to the DigitalOcean account. This code should
        eventually be purged
        """

        manager = digitalocean.Manager(token=self._token)
        return manager.get_all_sshkeys()

    def get_ssh_key_id(self, key):
        """
        Get the DigitalOcean ID for the SSH key. If the SSH key hasn't been
        uploaded to DigitalOcean, upload it.
        """

        if key.digitalocean_id:
            return key.digitalocean_id
        else:
            new_do_key = digitalocean.SSHKey(
                token=self._token,
                name='minecraftserver',
                public_key=key.public_key
            )
            new_do_key.create()
            key.digitalocean_id = new_do_key.id
            key.save(update_fields=['digitalocean_id'])
            return new_do_key.id

    def _set_status(self, msg):
        self.config.last_status = msg
        self.config.save(update_fields=['last_status'])

    def _create_droplet(self):
        "Create a new Digital Ocean Droplet"
        ssh_key_id = self.get_ssh_key_id(self.config.ssh_key)  # noqa: F841
        droplet = digitalocean.Droplet(
            token=self._token,
            name="MCServer-{}".format(self.config.id),
            region=self.region,
            image=self.image,
            size_slug=self.size,
            # TODO: Set this to use the key from `get_ssh_key_id`
            ssh_keys=self.get_ssh_keys(),
            # volumes=[volume.id],
            tags=['minecraftserver'],
            monitoring=True
        )
        droplet.create()
        self.droplet = droplet

    def _rebuild_droplet(self, fast: bool = False):
        droplet = digitalocean.Droplet.get_object(
            self._token,
            self.config.droplet_id
        )
        self.droplet = droplet
        if not fast:
            droplet.rebuild()
        else:
            with Connection(
                user='root',
                host=self.config.droplet_ip,
                connect_kwargs={'pkey': self.config.ssh_key.as_pkey()}
            ) as connection:
                connection.run('systemctl disable minecraft --now')
                connection.run('rm -rf /var/minecraft')

    def _rebuild_or_create_droplet(self, fast: bool = False):
        if not self.config.droplet_id:
            self._create_droplet()
        else:
            self._rebuild_droplet(fast=fast)

    def _wait_for_droplet(self):
        "Wait for the droplet to come online"
        # Get fresh status
        self.droplet.load()

        # Wait for status to become active
        time = 0
        while not self.droplet.status == 'active':
            time += self.poll_interval
            if time > self.timeout:
                raise DigitalOceanError("Timed out waiting for droplet to come up")
            sleep(self.poll_interval)
            self.droplet.load()

        # Stash the IP address in the config
        self.config.droplet_ip = self.droplet.ip_address
        self.config.save(update_fields=['droplet_ip'])

    def _run_install_script(self):
        "Run the install script. Intended to be run on a pristine droplet"
        install_file = StringIO(self.config.get_install_script())
        with Connection(
            user='root',
            host=self.config.droplet_ip,
            connect_kwargs={'pkey': self.config.ssh_key.as_pkey()}
        ) as connection:
            connection.put(install_file, 'install.sh')
            connection.run('chmod +x install.sh')
            connection.run('./install.sh')

    def _install_mods(self):
        if self.config.mods.count() < 1:
            return

        with Connection(
            user='root',
            host=self.config.droplet_ip,
            connect_kwargs={'pkey': self.config.ssh_key.as_pkey()}
        ) as connection:
            connection.run('mkdir -p /var/minecraft/server/mods')
            for mod in self.config.mods.all():
                connection.put(
                    mod.download_file,
                    '/var/minecraft/server/mods/{}'.format(mod.filename())
                )

    def _start_minecraft(self):
        "Start the Minecraft service. Expects a fully provisioned server"
        with Connection(
            user='root',
            host=self.config.droplet_ip,
            connect_kwargs={'pkey': self.config.ssh_key.as_pkey()}
        ) as connection:
            connection.run('chown minecraft /var/minecraft/server/ -R')
            connection.run('systemctl enable minecraft --now')

    def _stop_minecraft(self):
        "Start the Minecraft service. Expects a fully provisioned server"
        with Connection(
            user='root',
            host=self.config.droplet_ip,
            connect_kwargs={'pkey': self.config.ssh_key.as_pkey()}
        ) as connection:
            connection.run('systemctl disable minecraft --now')

    def rebuild_minecraft_droplet(self, fast: bool = False):
        self._set_status('Starting droplet')
        self._rebuild_or_create_droplet(fast=fast)

        self._set_status('Waiting for droplet boot')
        self._wait_for_droplet()

        self._set_status('Installing Minecraft server')
        self._run_install_script()

        self._set_status('Installing mods')
        self._install_mods()

        self._set_status('Starting Minecraft')
        self._start_minecraft()

        self._set_status('Server up')
        return self.droplet
