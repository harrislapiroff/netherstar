from django.db import models

from djocean.models import Image, Size
from minecraftserver.models.ssh import KeyPair


class SiteSettings(models.Model):
    permitted_do_images = models.ManyToManyField(
        Image,
        blank=True,
        related_name='+'
    )
    permitted_do_sizes = models.ManyToManyField(
        Size,
        blank=True,
        related_name='+'
    )

    default_minecraft_verion = models.ForeignKey(
        'minecraftserver.MinecraftVersion',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )
    default_keypair = models.ForeignKey(
        KeyPair,
        default=KeyPair.get_default_keypair,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name_plural = 'site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise NotImplementedError('Site Settings may not be deleted')

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Site Settings'
