from django.contrib import admin
from humanize import naturalsize

from djocean.models import Image, Region, Size


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'distribution',
        'name',
        'slug',
        'regions_display',
        'status',
    )

    def regions_display(self: 'ImageAdmin', instance: Image):
        return ', '.join([str(x) for x in instance.regions.all()])
    regions_display.short_description = 'regions'


class RegionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'available',
        'features',
    )


class SizeAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'memory_size_display',
        'disk_size_display',
        'vcpus',
        'available',
        'price_monthly',
        'price_hourly',
        'regions_display',
    )

    def regions_display(self: 'SizeAdmin', instance: Image):
        return ', '.join([str(x) for x in instance.regions.all()])
    regions_display.short_description = 'regions'

    def disk_size_display(self: 'SizeAdmin', instance: Size):
        # multiply by 1000^2 to convert to kb, then format
        return naturalsize(instance.disk * 1000 * 1000)
    disk_size_display.short_description = 'disk size'

    def memory_size_display(self: 'SizeAdmin', instance: Size):
        # multiply by 1024^2 to convert to kib, then format
        # even though DO's docs say they measure in megabytes, I suspect they
        # are using gibibytes because that math makes the numbers match the
        # names
        return naturalsize(instance.memory * 1024 * 1024, binary=True)
    memory_size_display.short_description = 'memory'


admin.site.register(Image, ImageAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Size, SizeAdmin)
