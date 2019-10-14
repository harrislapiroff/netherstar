import os

from django.db import models

from minecraftserver.utils.digitalocean import dropletmanager
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

    def __str__(self: 'MinecraftModVersion') -> str:
        return '{}: {}'.format(
            self.mod,
            os.path.basename(self.download_file.name)
        )


def default_minecraft_version_id():
    return MinecraftVersion.objects.all()[0].pk


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
        related_name='+'
    )
    droplet_id = models.PositiveIntegerField(blank=True, null=True)

    def create_droplet(self: 'MinecraftServerConfig'):
        droplet = dropletmanager.create_minecraft_droplet(self)
        self.droplet_id = droplet.id
        self.save()

    def get_install_script(self: 'MinecraftServerConfig'):
        return install_script_for_config(self)

    def __str__(self: 'MinecraftServerConfig') -> str:
        return self.name
