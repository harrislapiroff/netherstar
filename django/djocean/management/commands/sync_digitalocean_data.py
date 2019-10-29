from decimal import Decimal

import digitalocean
from dateutil.parser import isoparse
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from djocean.models import Region, Image, Size


class Command(BaseCommand):
    help = 'Sync DigitalOcean data from the DigitalOcean API'

    def handle(self, *args, **options):
        do = digitalocean.Manager(token=settings.DIGITALOCEAN_TOKEN)

        # Regions
        with transaction.atomic():
            self.stdout.write('Syncing regions...')
            regions = do.get_all_regions()
            for region in regions:
                obj, created = Region.objects.update_or_create(
                    {
                        'slug': region.slug,
                        'name': region.name,
                        'features': region.features,
                        'available': region.available,
                    },
                    slug=region.slug
                )
                self.stdout.write('- {} {}'.format(
                    region.name,
                    'created' if created else 'updated'
                ))

        # Images
        with transaction.atomic():
            self.stdout.write('Syncing images...')
            images = do.get_images(type='distribution')
            for image in images:
                obj, created = Image.objects.update_or_create(
                    {
                        'do_id': image.id,
                        'name': image.name,
                        'type': image.type,
                        'distribution': image.distribution,
                        'slug': image.slug,
                        'public': image.public,
                        'created_at': isoparse(image.created_at),
                        'min_disk_size': image.min_disk_size,
                        'size_gigabytes': image.size_gigabytes,
                        'description': image.description,
                        'tags': image.tags,
                        'status': image.status,
                        'error_message': image.error_message,
                    },
                    do_id=image.id
                )
                obj.regions.set(Region.objects.filter(slug__in=image.regions))
                self.stdout.write('- {} {}'.format(
                    image.name,
                    'created' if created else 'updated'
                ))

        # Sizes
        with transaction.atomic():
            self.stdout.write('Syncing sizes...')
            sizes = do.get_all_sizes()
            for size in sizes:
                obj, created = Size.objects.update_or_create(
                    {
                        'slug': size.slug,
                        'available': size.available,
                        'transfer': size.transfer,
                        'price_monthly': Decimal(size.price_monthly),
                        'price_hourly': size.price_hourly,
                        'memory': size.memory,
                        'vcpus': size.vcpus,
                        'disk': size.disk,
                    },
                    slug=size.slug
                )
                obj.regions.set(Region.objects.filter(slug__in=size.regions))
                self.stdout.write('- {} {}'.format(
                    size.slug,
                    'created' if created else 'updated'
                ))
