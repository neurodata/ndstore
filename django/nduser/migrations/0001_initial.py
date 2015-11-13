# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('backup_id', models.AutoField(serialize=False, primary_key=True)),
                ('protocol', models.CharField(max_length=255, choices=[(b'local', b'file system'), (b's3', b'Amazon S3')])),
                ('filename', models.CharField(max_length=4096)),
                ('jsonfile', models.CharField(max_length=4096)),
                ('description', models.CharField(default=b'', max_length=4096)),
                ('datetimestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Done'), (1, b'Processing'), (2, b'Failed')])),
            ],
            options={
                'db_table': 'backups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel_name', models.CharField(max_length=255)),
                ('channel_description', models.CharField(max_length=4096, blank=True)),
                ('channel_type', models.CharField(max_length=255, choices=[(b'image', b'IMAGES'), (b'annotation', b'ANNOTATIONS'), (b'timeseries', b'TIMESERIES')])),
                ('resolution', models.IntegerField(default=0)),
                ('propagate', models.IntegerField(default=0, choices=[(0, b'NOT PROPAGATED'), (2, b'PROPAGATED')])),
                ('channel_datatype', models.CharField(max_length=255, choices=[(b'uint8', b'uint8'), (b'uint16', b'uint16'), (b'uint32', b'uint32'), (b'uint64', b'uint64'), (b'float32', b'float32')])),
                ('readonly', models.IntegerField(default=0, choices=[(1, b'Yes'), (0, b'No')])),
                ('exceptions', models.IntegerField(default=0, choices=[(1, b'Yes'), (0, b'No')])),
                ('startwindow', models.IntegerField(default=0)),
                ('endwindow', models.IntegerField(default=0)),
                ('default', models.BooleanField(default=False)),
                ('header', models.CharField(default=b'', max_length=8192, blank=True)),
            ],
            options={
                'db_table': 'channels',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('dataset_name', models.CharField(max_length=255, serialize=False, verbose_name=b'Name of the Image dataset', primary_key=True)),
                ('dataset_description', models.CharField(max_length=4096, blank=True)),
                ('public', models.IntegerField(default=0, choices=[(0, b'Private'), (1, b'Public')])),
                ('ximagesize', models.IntegerField()),
                ('yimagesize', models.IntegerField()),
                ('zimagesize', models.IntegerField()),
                ('xoffset', models.IntegerField(default=0)),
                ('yoffset', models.IntegerField(default=0)),
                ('zoffset', models.IntegerField(default=0)),
                ('xvoxelres', models.FloatField(default=1.0)),
                ('yvoxelres', models.FloatField(default=1.0)),
                ('zvoxelres', models.FloatField(default=1.0)),
                ('scalingoption', models.IntegerField(default=0, choices=[(0, b'Z Slices'), (1, b'Isotropic')])),
                ('scalinglevels', models.IntegerField(default=0)),
                ('starttime', models.IntegerField(default=0)),
                ('endtime', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'datasets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_name', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('project_description', models.CharField(max_length=4096, blank=True)),
                ('public', models.IntegerField(default=0, choices=[(0, b'Private'), (1, b'Public')])),
                ('host', models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063'), (b'localhost', b'Debug')])),
                ('kvengine', models.CharField(default=b'MySQL', max_length=255, choices=[(b'MySQL', b'MySQL'), (b'Cassandra', b'Cassandra'), (b'Riak', b'Riak')])),
                ('kvserver', models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063'), (b'localhost', b'Debug')])),
                ('nd_version', models.CharField(default=b'0.6', max_length=255)),
                ('schema_version', models.CharField(default=b'0.6', max_length=255)),
                ('dataset', models.ForeignKey(to='nduser.Dataset')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projects',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('token_name', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('token_description', models.CharField(max_length=4096, blank=True)),
                ('public', models.IntegerField(default=0, choices=[(0, b'Private'), (1, b'Public')])),
                ('project', models.ForeignKey(to='nduser.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tokens',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='NIFTIHeader',
            fields=[
                ('channel', models.OneToOneField(primary_key=True, serialize=False, to='nduser.Channel')),
                ('header', models.BinaryField(max_length=1024)),
                ('affine', models.BinaryField(max_length=1024)),
            ],
            options={
                'db_table': 'nifti_header',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='channel',
            name='project',
            field=models.ForeignKey(to='nduser.Project'),
        ),
        migrations.AddField(
            model_name='backup',
            name='channel',
            field=models.ForeignKey(blank=True, to='nduser.Channel', null=True),
        ),
        migrations.AddField(
            model_name='backup',
            name='project',
            field=models.ForeignKey(to='nduser.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='channel',
            unique_together=set([('project', 'channel_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='backup',
            unique_together=set([('project', 'datetimestamp')]),
        ),
    ]
