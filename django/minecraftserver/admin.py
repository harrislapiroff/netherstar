from django.contrib import admin
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.urls import reverse

from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from minecraftserver.models import MinecraftServerConfig
from minecraftserver.models import MinecraftVersion
from minecraftserver.models import ForgeVersion
from minecraftserver.models import MinecraftMod
from minecraftserver.models import MinecraftModVersion
from minecraftserver.models import KeyPair
from minecraftserver.models import SiteSettings
from minecraftserver.utils.digitalocean import DigitalOceanProvider


class MinecraftServerAdmin(admin.ModelAdmin):
    readonly_fields = (
        'droplet_id',
        'droplet_ip',
        'last_status',
        'install_script',
    )
    actions = (
        'restart_servers',
        'rebuild_servers',
    )
    list_display = (
        'name',
        'version',
        'last_status',
    )
    filter_horizontal = (
        'mods',
    )

    def install_script(self, instance: MinecraftServerConfig) -> str:
        "Get the install script HTML formatted for display"
        html_formatter = HtmlFormatter(cssclass="install-script")
        return mark_safe(
            "".join([
                highlight(
                    instance.get_install_script(),
                    BashLexer(),
                    html_formatter
                ),
                "<style type=\"text/css\">",
                ".install-script { padding: 5px 10px; border-radius: 4px; }",
                html_formatter.get_style_defs(),
                "</style>",
            ])
        )

    def restart_servers(self, request, queryset) -> list:
        "Start the Docker container"
        for instance in queryset.all():
            DigitalOceanProvider(instance).rebuild_minecraft_droplet(fast=True)
    restart_servers.short_description = 'Restart Servers'

    def rebuild_servers(self, request, queryset) -> list:
        "Start the Docker container"
        for instance in queryset.all():
            DigitalOceanProvider(instance).rebuild_minecraft_droplet()
    rebuild_servers.short_description = 'Rebuild Servers'


class MinecraftVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_url', 'release_time')


class MinecraftModVersionInline(admin.TabularInline):
    model = MinecraftModVersion
    min_num = 1
    extra = 0
    verbose_name = 'version'
    verbose_name_plural = 'versions'
    filter_horizontal = (
        'compatible_with',
    )


class MinecraftModAdmin(admin.ModelAdmin):
    inlines = (
        MinecraftModVersionInline,
    )


class ForgeVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'minecraft_version', 'download_url')

    def minecraft_version(self, instance: ForgeVersion) -> str:
        return self.minecraft_version.name


class SiteSettingsAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'permitted_do_images',
        'permitted_do_sizes',
    )

    def changelist_view(self, *args, **kwargs):
        sitesettings = SiteSettings.load()
        return redirect(reverse(
            'admin:minecraftserver_sitesettings_change',
            args=[sitesettings.pk]
        ))

    def has_delete_permission(self, request, instance=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(MinecraftVersion, MinecraftVersionAdmin)
admin.site.register(ForgeVersion, ForgeVersionAdmin)
admin.site.register(MinecraftMod, MinecraftModAdmin)
admin.site.register(MinecraftServerConfig, MinecraftServerAdmin)
admin.site.register(KeyPair)
admin.site.register(SiteSettings, SiteSettingsAdmin)
