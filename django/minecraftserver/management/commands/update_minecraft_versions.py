import requests
from dateutil.parser import isoparse
from django.core.management.base import BaseCommand
from django.db import transaction

from minecraftserver.models import MinecraftVersion


class Command(BaseCommand):
    help = 'Get a list of available Minecraft versions from Mojang to store in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            nargs='?',
            default='https://launchermeta.mojang.com/mc/game/version_manifest.json'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        version_data = requests.get(options['url']).json()
        # For now we only include releases, not snapshots
        releases = filter(
            lambda r: r['type'] == 'release',
            version_data['versions']
        )
        for release in releases:
            release_data = requests.get(release['url']).json()
            # Old versions of minecraft have no server and we won't include them
            if 'server' in release_data['downloads']:
                _, created = MinecraftVersion.objects.update_or_create(
                    {
                        'name': release['id'],
                        'download_url': release_data['downloads']['server']['url'],
                        'release_time': isoparse(release['releaseTime']),
                    },
                    name=release['id']
                )
                self.stdout.write(
                    'Release {:10} {}'.format(
                        release['id'],
                        self.style.SUCCESS('created') if created else self.style.NOTICE('exists')
                    )
                )
