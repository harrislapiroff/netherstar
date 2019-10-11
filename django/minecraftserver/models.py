from django.db import models

from minecraftserver.utils.digitalocean import dropletmanager


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


def default_minecraft_version_id():
    return MinecraftVersion.objects.all()[0].pk


class MinecraftServer(models.Model):
    name = models.CharField(max_length=50)

    eula_accepted = models.BooleanField()
    version = models.ForeignKey(
        MinecraftVersion,
        default=default_minecraft_version_id,
        on_delete=models.PROTECT,
        related_name='servers'
    )
    forge = models.BooleanField()

    droplet_id = models.PositiveIntegerField(blank=True, null=True)

    def create_droplet(self):
        droplet = dropletmanager.create_minecraft_droplet(self)
        self.droplet_id = droplet.id
        self.save()

    def __str__(self: 'MinecraftServer') -> str:
        return self.name
