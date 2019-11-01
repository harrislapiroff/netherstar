import os

from django.core.exceptions import ValidationError
from django.db import models

from djocean.models import Image, Size, Region
from minecraftserver.models.ssh import KeyPair
from minecraftserver.utils.provisioning import install_script_for_config
from minecraftserver.utils.sitesettings import allowed_images_q
from minecraftserver.utils.sitesettings import allowed_sizes_q
from minecraftserver.utils.sitesettings import default_minecraft_version_id
from minecraftserver.utils.sitesettings import default_keypair


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
    minecraft_version = models.ForeignKey(
        MinecraftVersion,
        help_text='Supported Minecraft version',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='forge_versions'
    )
    latest = models.BooleanField()
    recommended = models.BooleanField()

    class Meta:
        ordering = ('-minecraft_version__release_time', 'pk')

    def __str__(self: 'ForgeVersion'):
        result = '{}-{}'.format(self.minecraft_version.name, self.name)
        if self.latest and self.recommended:
            result = result + ' (Latest, Recommended)'
        elif self.latest:
            result = result + ' (Latest)'
        elif self.recommended:
            result = result + ' (Recommended)'
        return result


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
    forge_version = models.ForeignKey(
        ForgeVersion,
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.PROTECT
    )
    mods = models.ManyToManyField(
        MinecraftModVersion,
        blank=True,
        related_name='+'
    )

    # DigitalOcean configuration
    droplet_image = models.ForeignKey(
        Image,
        limit_choices_to=allowed_images_q,
        related_name='+',
        on_delete=models.PROTECT
    )
    droplet_size = models.ForeignKey(
        Size,
        limit_choices_to=allowed_sizes_q,
        related_name='+',
        on_delete=models.PROTECT
    )
    droplet_region = models.ForeignKey(
        Region,
        related_name='+',
        on_delete=models.PROTECT
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

    def clean(self):
        errors = []
        if self.droplet_region not in self.droplet_image.regions.all():
            error_message = 'Image {} not available in region {}'.format(
                self.droplet_image,
                self.droplet_region
            )
            errors.append({'region': error_message})
        if self.droplet_region not in self.droplet_size.regions.all():
            error_message = 'Size {} not available in region {}'.format(
                self.droplet_size,
                self.droplet_region
            )
            errors.append({'region': error_message})
        if errors:
            raise ValidationError(errors)

    def get_install_script(self: 'MinecraftServerConfig'):
        return install_script_for_config(self)

    def __str__(self: 'MinecraftServerConfig') -> str:
        return self.name
