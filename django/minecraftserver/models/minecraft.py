import os

from django.db import models

from minecraftserver.models.ssh import KeyPair
from minecraftserver.models.sitesettings import SiteSettings
from minecraftserver.utils.provisioning import install_script_for_config


class MinecraftVersion(models.Model):
    name = models.CharField(max_length=50)
    download_url = models.URLField()
    release_time = models.DateTimeField()

    class Meta:
        ordering = ('-release_time',)

    def __str__(self: 'MinecraftVersion'):
        return self.name


class ForgeVersion(models.Model):
    name = models.CharField(max_length=50)
    download_url = models.URLField()
    minecraft_version = models.OneToOneField(
        MinecraftVersion,
        help_text='Supported Minecraft version',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='forge_version'
    )

    class Meta:
        ordering = ('-minecraft_version__release_time',)

    def __str__(self: 'ForgeVersion'):
        return self.name


class MinecraftMod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self: 'MinecraftMod') -> str:
        return self.name


class MinecraftModVersion(models.Model):
    mod = models.ForeignKey(
        MinecraftMod,
        related_name='versions',
        on_delete=models.CASCADE
    )
    download_file = models.FileField()
    compatible_with = models.ManyToManyField(
        MinecraftVersion,
        related_name='+'
    )

    def filename(self: 'MinecraftModVersion') -> str:
        return os.path.basename(self.download_file.name)

    def __str__(self: 'MinecraftModVersion') -> str:
        return '{}: {}'.format(
            self.mod,
            self.filename()
        )


def default_minecraft_version_id():
    return SiteSettings.load().default_minecraft_verion


def default_keypair():
    return SiteSettings.load().default_keypair


class MinecraftServerConfig(models.Model):
    """
    Configuration details for a Minecraft server
    """

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    version = models.ForeignKey(
        MinecraftVersion,
        default=default_minecraft_version_id,
        on_delete=models.PROTECT,
        related_name='servers'
    )
    forge = models.BooleanField()
    mods = models.ManyToManyField(
        MinecraftModVersion,
        blank=True,
        related_name='+'
    )

    # These fields are for site admin configuration only
    ssh_key = models.ForeignKey(
        KeyPair,
        default=default_keypair,
        blank=True,
        null=True,
        verbose_name='SSH key',
        on_delete=models.SET_NULL
    )

    # These fields should be read only in any interface
    droplet_id = models.PositiveIntegerField(blank=True, null=True)
    droplet_ip = models.GenericIPAddressField(blank=True, null=True)
    last_status = models.TextField(blank=True, null=True)

    def get_install_script(self: 'MinecraftServerConfig'):
        return install_script_for_config(self)

    def __str__(self: 'MinecraftServerConfig') -> str:
        return self.name
