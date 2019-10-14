# Generated by Django 2.2.6 on 2019-10-14 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minecraftserver', '0002_auto_20191014_1800'),
    ]

    operations = [
        migrations.AddField(
            model_name='minecraftserverconfig',
            name='droplet_ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='minecraftserverconfig',
            name='last_status',
            field=models.TextField(blank=True, null=True),
        ),
    ]
