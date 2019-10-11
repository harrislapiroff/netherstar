from typing import Optional

import digitalocean
from django.conf import settings

from minecraftserver.utils.provisioning import FORGE_INSTALL_SCRIPT
from minecraftserver.utils.provisioning import VANILLA_INSTALL_SCRIPT


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
        mc_version = config.version
        INSTALL_SCRIPT_TEMPLATE = VANILLA_INSTALL_SCRIPT
        context = {
            'minecraft_download_url': mc_version.download_url,
            'minecraft_filename': mc_version.download_url.split('/')[-1],
        }

        if config.forge:
            forge_version = config.version.forge_version
            context.update({
                'forge_installer_url': forge_version.download_url,
                'forge_installer_filename': forge_version.download_url.split('/')[-1],
                # Can we deduce the filename with more confidence?
                'forge_filename': forge_version.download_url.split('/')[-1].replace('-installer', '')
            })
            INSTALL_SCRIPT_TEMPLATE = FORGE_INSTALL_SCRIPT

        install_script = INSTALL_SCRIPT_TEMPLATE.format(**context)

        # TODO: check for an existing volume and use it. We should *never*
        # create a new volume for a particular MinecraftServer instance
        volume = digitalocean.Volume(
            token=self._token,
            region=self.region,
            filesystem_type='ext4',
            filesystem_label='volume{}label'.format(config.id),
            name="MCServer-volume-{}".format(config.id),
            description='Volume for MCServer-{}'.format(config.id),
            size_gigabytes=1,
            tags=['minecraftserver']
        )
        volume.create()

        droplet = digitalocean.Droplet(
            token=self._token,
            name="MCServer-{}".format(config.id),
            region=self.region,
            image=self.image,
            size_slug=self.size,
            user_data=install_script,
            ssh_keys=self.get_ssh_keys(),
            volumes=[volume.id],
            tags=['minecraftserver'],
            monitoring=True
        )
        droplet.create()
        return droplet


dropletmanager = DigitalOceanProvider(token=settings.DIGITALOCEAN_TOKEN)
