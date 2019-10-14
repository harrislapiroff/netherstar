from io import StringIO
import sys
from time import sleep
from typing import Optional

import digitalocean
from django.conf import settings
from fabric import Connection

from minecraftserver.models.ssh import KeyPair

class DigitalOceanError(Exception):
    pass


class DigitalOceanProvider:
    tag = "minecraftserver"
    region = "nyc1"
    image = "debian-9-x64"
    size = "s-2vcpu-4gb"

    poll_interval = 5
    timeout = 600

    def __init__(self, token: Optional[str] = None):
        self._token = token if token else settings.DIGITALOCEAN_TOKEN

    def get_ssh_keys(self):
        """
        Get all keys registered to the DigitalOcean account. This should
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

    def create_minecraft_droplet(self, config):
        ssh_key_id = self.get_ssh_key_id(config.ssh_key)

        droplet = digitalocean.Droplet(
            token=self._token,
            name="MCServer-{}".format(config.id),
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

        config.last_status = "Waiting for droplet..."
        config.save(update_fields=['last_status'])

        # Wait for the droplet to come up
        time = 0
        while not droplet.status == 'active':
            droplet.load()
            time += self.poll_interval
            if time > self.timeout:
                config.last_status = "Timed out waiting for droplet to come up"
                config.save(update_fields=['last_status'])
                raise DigitalOceanError("Timed out waiting for droplet to come up")
            sleep(self.poll_interval)

        # Stash the IP address in the config
        config.droplet_ip = droplet.ip_address
        config.last_status = "Droplet started. Provisioning server"
        config.save(update_fields=['droplet_ip', 'last_status'])

        # Put the install script on the droplet and run it
        install_file = StringIO(config.get_install_script())
        with Connection(
            user='root',
            host=config.droplet_ip,
            connect_kwargs={'pkey': config.ssh_key.as_pkey()}
        ) as connection:
            connection.put(install_file, 'install.sh')
            connection.run('chmod +x install.sh')
            connection.run('./install.sh')

        return droplet


dropletmanager = DigitalOceanProvider(token=settings.DIGITALOCEAN_TOKEN)
