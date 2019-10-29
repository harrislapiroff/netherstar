from django.db import models
from django.contrib.postgres.fields import ArrayField


class Region(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    available = models.BooleanField()
    features = ArrayField(models.CharField(max_length=255))

    def __str__(self):
        return self.name


class Image(models.Model):
    NEW = 'NEW'
    AVAILABLE = 'available'
    PENDING = 'pending'
    DELETED = 'deleted'
    STATUS_CHOICES = (
        (NEW, NEW),
        (AVAILABLE, AVAILABLE),
        (PENDING, PENDING),
        (DELETED, DELETED),
    )

    SNAPSHOT = 'snapshot'
    BACKUP = 'backup'
    CUSTOM = 'custom'
    TYPE_CHOICES = (
        (SNAPSHOT, SNAPSHOT),
        (BACKUP, BACKUP),
        (CUSTOM, CUSTOM),
    )

    do_id = models.PositiveIntegerField(
        'DigitalOcean ID',
        unique=True
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    distribution = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        null=True,
        blank=True
    )
    public = models.BooleanField()
    regions = models.ManyToManyField(Region, blank=True)
    created_at = models.DateTimeField()
    min_disk_size = models.PositiveIntegerField()
    size_gigabytes = models.FloatField()
    description = models.TextField(null=True, blank=True)
    tags = ArrayField(
        models.CharField(max_length=255),
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    available = models.BooleanField()
    transfer = models.FloatField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_hourly = models.FloatField()
    memory = models.PositiveIntegerField()
    vcpus = models.PositiveIntegerField()
    disk = models.PositiveIntegerField()
    regions = models.ManyToManyField(Region, blank=True)

    class Meta:
        ordering = ['price_hourly']

    def __str__(self):
        return self.slug
