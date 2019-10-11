from urllib.parse import urlparse

from requests_html import HTMLSession
from dateutil.parser import isoparse
from django.core.management.base import BaseCommand
from django.db import transaction

from minecraftserver.models import ForgeVersion, MinecraftVersion


FORGE_RESULT_STRING = 'Forge Version {:25} {}'

class Command(BaseCommand):
    help = 'Get a list of available Forge versions from minecraftforge.net to store in database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            nargs='?',
            default='http://files.minecraftforge.net/'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        parsed_url = urlparse(options['url'])

        session = HTMLSession()
        response = session.get(options['url'])
        version_page_links = response.html.find('.li-version-list .nav-collapsible li a')
        version_page_urls = [(x.text, x.attrs['href']) for x in version_page_links]

        # Buckle up for some serious website scraping. The Forge ecosystem is
        # a beautiful beautiful mess

        # For each version we have to get the version's HTML page to find the
        # download URL
        for mc_name, url in version_page_urls:
            full_url = '{}://{}{}'.format(
                parsed_url.scheme,
                parsed_url.netloc,
                url
            )
            response = session.get(full_url)
            download_divs = response.html.find('.download')

            # Determine the recommended download div
            try:
                # Try to track down the download box labelled recommended
                recommended_download_div = filter(
                    lambda div: 'Recommended' in div.find('.title', first=True).text,
                    download_divs
                ).__next__()
            except StopIteration:
                # Otherwise assume the last box in the HTML is the recommended one
                recommended_download_div = download_divs[-1]

            try:
                version_name = recommended_download_div.find('small', first=True).text
                minecraft_version = MinecraftVersion.objects.get(name=mc_name)
                download_url = '{}://{}{}'.format(
                    parsed_url.scheme,
                    parsed_url.netloc,
                    recommended_download_div.find('a[title="Installer"]', first=True).attrs['href']
                )
            except MinecraftVersion.DoesNotExist:
                # If we don't offer a matching version of Minecraft, don't create a Forge version object
                self.stdout.write(
                    FORGE_RESULT_STRING.format(
                        version_name,
                        self.style.ERROR('matching Minecraft version {} not found'.format(mc_name))
                    )
                )
                continue
            except AttributeError:
                # AttributeError suggests there's no installer link on the page
                self.stdout.write(
                    FORGE_RESULT_STRING.format(
                        version_name,
                        self.style.ERROR('installer not found'.format(mc_name))
                    )
                )
                self.stdout.write(
                    'Assuming older Forge versions have no installer and terminating. ' +
                    self.style.SUCCESS('OK')
                )
                break

            # Let's only store one version of Forge per Minecraft version
            # Not a ton of value to storing old versions of Forge
            _, created = ForgeVersion.objects.update_or_create(
                {
                    'name': version_name,
                    'download_url': download_url,
                    'minecraft_version': minecraft_version,
                },
                minecraft_version__name=mc_name
            )

            self.stdout.write(
                FORGE_RESULT_STRING.format(
                    version_name,
                    self.style.SUCCESS('created') if created else self.style.NOTICE('exists')
                )
            )
