from typing import Optional

import digitalocean
from django.conf import settings


class DigitalOceanProvider:
    tag = "minecraftserver"
    region = "nyc1"
    image = "debian-9-x64"
    size = "s-2vcpu-4gb"

    def __init__(self, token: Optional[str] = None):
        self._token = token if token else settings.DIGITALOCEAN_TOKEN

    def get_ssh_keys(self):
        manager = digitalocean.Manager(token=self._token)
        return manager.get_all_sshkeys()

    def create_minecraft_droplet(self, config):
        install_script = config.get_install_script()

        droplet = digitalocean.Droplet(
            token=self._token,
            name="MCServer-{}".format(config.id),
            region=self.region,
            image=self.image,
            size_slug=self.size,
            user_data=install_script,
            ssh_keys=self.get_ssh_keys(),
            # volumes=[volume.id],
            tags=['minecraftserver'],
            monitoring=True
        )
        droplet.create()
        return droplet


dropletmanager = DigitalOceanProvider(token=settings.DIGITALOCEAN_TOKEN)
