from urllib.parse import urlparse

from requests_html import HTMLSession
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

        # Get the list of links from the sidebar for different minecraft
        # versions
        version_page_links = response.html.find('.li-version-list .nav-collapsible li a')
        version_page_urls = [(x.text, x.attrs['href']) for x in version_page_links]
        # Add the current URL, which is the list for the current version of
        # minecraft
        active_page_item = response.html.find(
            '.li-version-list .nav-collapsible .elem-active',
            first=True
        )
        version_page_urls = [(active_page_item.text, parsed_url.path)] + version_page_urls

        # Buckle up for some serious website scraping. The Forge ecosystem is
        # a beautiful beautiful mess

        # For each minecraft version we have to get the version's HTML page to
        # find the download URL
        for mc_name, url in version_page_urls:
            try:
                # Get the corresponding Minecraft version
                minecraft_version = MinecraftVersion.objects.get(name=mc_name)
            except MinecraftVersion.DoesNotExist:
                # If we don't offer a matching version of Minecraft, don't
                # create Forge versions
                self.stdout.write(
                    FORGE_RESULT_STRING.format(
                        '{}-*'.format(mc_name),
                        self.style.ERROR('matching Minecraft version {} not found'.format(mc_name))
                    )
                )
                continue

            # Generate the URL to request and request it
            full_url = '{}://{}{}'.format(
                parsed_url.scheme,
                parsed_url.netloc,
                url
            )
            response = session.get(full_url)

            # Determine the recommended and latest download divs
            download_divs = response.html.find('.download')
            try:
                # Try to track down the download box labelled recommended
                recommended_download_path = filter(
                    lambda div: 'Recommended' in div.find('.title', first=True).text,
                    download_divs
                ).__next__()\
                 .find('a[title="Installer"]', first=True)\
                 .attrs['href']
            except (StopIteration, AttributeError):
                recommended_download_path = None
            try:
                # Try to track down the download box labelled latest
                latest_download_path = filter(
                    lambda div: 'Latest' in div.find('.title', first=True).text,
                    download_divs
                ).__next__()\
                 .find('a[title="Installer"]', first=True)\
                 .attrs['href']
            except (StopIteration, AttributeError):
                latest_download_path = None

            # Iterate through every table row on the page to record the version
            forge_version_rows = response.html.find('.download-list tbody tr')
            for row in forge_version_rows:
                version_name = row.find(
                    '.download-version',
                    first=True
                ).text.strip()
                installer_link = row.xpath(
                    '//a[contains(string(), "Installer")]',
                    first=True
                )

                if installer_link is None:
                    self.stdout.write(
                        FORGE_RESULT_STRING.format(
                            version_name,
                            self.style.ERROR('installer not found'.format(mc_name))
                        )
                    )
                    continue

                installer_path = installer_link.attrs['href']
                download_url = '{}://{}{}'.format(
                    parsed_url.scheme,
                    parsed_url.netloc,
                    installer_path
                )
                _, created = ForgeVersion.objects.update_or_create(
                    {
                        'name': version_name,
                        'download_url': download_url,
                        'minecraft_version': minecraft_version,
                        # If it matches the path for the recommended download
                        'recommended': recommended_download_path == installer_path,
                        # If it matches the path for the latest download
                        'latest': latest_download_path == installer_path,
                    },
                    name=version_name
                )

                self.stdout.write(
                    FORGE_RESULT_STRING.format(
                        '{}-{}'.format(mc_name, version_name),
                        self.style.SUCCESS('created') if created else self.style.NOTICE('exists')
                    )
                )
