from django.db.models import Q
from minecraftserver.models.sitesettings import SiteSettings


def allowed_images_q():
    site_settings = SiteSettings.load()
    return Q(id__in=site_settings.permitted_do_images.values_list(
        'id',
        flat=True
    ))


def allowed_sizes_q():
    site_settings = SiteSettings.load()
    return Q(id__in=site_settings.permitted_do_sizes.values_list(
        'id',
        flat=True
    ))


def default_minecraft_version_id():
    return SiteSettings.load().default_minecraft_verion


def default_keypair():
    return SiteSettings.load().default_keypair
