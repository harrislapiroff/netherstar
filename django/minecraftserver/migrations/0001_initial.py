# Generated by Django 2.2.6 on 2019-10-31 04:54

from django.db import migrations, models
import django.db.models.deletion
import minecraftserver.models.minecraft
import minecraftserver.models.ssh


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('djocean', '0002_auto_20191029_0506'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForgeVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('download_url', models.URLField()),
                ('latest', models.BooleanField()),
                ('recommended', models.BooleanField()),
            ],
            options={
                'ordering': ('-minecraft_version__release_time',),
            },
        ),
        migrations.CreateModel(
            name='KeyPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.TextField()),
                ('private_key', models.TextField()),
                ('digitalocean_id', models.PositiveIntegerField(blank=True, null=True)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        migrations.CreateModel(
            name='MinecraftMod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MinecraftModVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='MinecraftVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('download_url', models.URLField()),
                ('release_time', models.DateTimeField()),
            ],
            options={
                'ordering': ('-release_time',),
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_keypair', models.ForeignKey(default=minecraftserver.models.ssh.KeyPair.get_default_keypair, on_delete=django.db.models.deletion.PROTECT, to='minecraftserver.KeyPair')),
                ('default_minecraft_verion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='minecraftserver.MinecraftVersion')),
                ('permitted_do_images', models.ManyToManyField(blank=True, related_name='_sitesettings_permitted_do_images_+', to='djocean.Image')),
                ('permitted_do_sizes', models.ManyToManyField(blank=True, related_name='_sitesettings_permitted_do_sizes_+', to='djocean.Size')),
            ],
            options={
                'verbose_name_plural': 'site settings',
            },
        ),
        migrations.CreateModel(
            name='MinecraftServerConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('droplet_id', models.PositiveIntegerField(blank=True, null=True)),
                ('droplet_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('last_status', models.TextField(blank=True, null=True)),
                ('forge_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='minecraftserver.ForgeVersion')),
                ('mods', models.ManyToManyField(blank=True, related_name='_minecraftserverconfig_mods_+', to='minecraftserver.MinecraftModVersion')),
                ('ssh_key', models.ForeignKey(blank=True, default=minecraftserver.models.minecraft.default_keypair, null=True, on_delete=django.db.models.deletion.SET_NULL, to='minecraftserver.KeyPair', verbose_name='SSH key')),
                ('version', models.ForeignKey(default=minecraftserver.models.minecraft.default_minecraft_version_id, on_delete=django.db.models.deletion.PROTECT, related_name='servers', to='minecraftserver.MinecraftVersion')),
            ],
        ),
        migrations.AddField(
            model_name='minecraftmodversion',
            name='compatible_with',
            field=models.ManyToManyField(related_name='_minecraftmodversion_compatible_with_+', to='minecraftserver.MinecraftVersion'),
        ),
        migrations.AddField(
            model_name='minecraftmodversion',
            name='mod',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='minecraftserver.MinecraftMod'),
        ),
        migrations.AddField(
            model_name='forgeversion',
            name='minecraft_version',
            field=models.ForeignKey(blank=True, help_text='Supported Minecraft version', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forge_versions', to='minecraftserver.MinecraftVersion'),
        ),
    ]
