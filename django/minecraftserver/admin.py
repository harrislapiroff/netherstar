from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from minecraftserver.models import MinecraftServer
from minecraftserver.models import MinecraftVersion
from minecraftserver.models import ForgeVersion


class MinecraftServerAdmin(admin.ModelAdmin):
    readonly_fields = (
        'container_status',
        'install_script',
    )
    actions = (
        'container_start',
        'container_stop',
    )
    list_display = (
        'name',
        'eula_accepted',
        'version',
    )

    def container_status(self, instance: MinecraftServer) -> str:
        "Get the status of the Docker container"
        return 'Unimplemented'
    container_status.short_description = 'Container Status'

    def install_script(self, instance: MinecraftServer) -> str:
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

    def container_start(self, request, queryset) -> list:
        "Start the Docker container"
        for instance in queryset.all():
            instance.create_droplet()
    container_start.short_description = 'Start Servers'

    def container_stop(self, request, queryset) -> list:
        pass
    container_stop.short_description = 'Stop Servers'


class MinecraftVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_url', 'release_time')


class ForgeVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'minecraft_version', 'download_url')

    def minecraft_version(self, instance: ForgeVersion) -> str:
        return self.minecraft_version.name


admin.site.register(MinecraftVersion, MinecraftVersionAdmin)
admin.site.register(ForgeVersion, ForgeVersionAdmin)
admin.site.register(MinecraftServer, MinecraftServerAdmin)
