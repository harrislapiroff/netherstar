from django.contrib import admin

from djocean.models import Image, Region, Size


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
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


admin.site.register(Image, ImageAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Size, SizeAdmin)
