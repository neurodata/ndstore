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
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel_name', models.CharField(max_length=255)),
                ('channel_description', models.CharField(max_length=4096, blank=True)),
                ('channel_type', models.CharField(max_length=255, choices=[(b'image', b'IMAGES'), (b'annotation', b'ANNOTATIONS'), (b'probmap', b'PROBABILITY_MAP'), (b'rgb', b'RGB'), (b'timeseries', b'TIMESERIES')])),
                ('resolution', models.IntegerField(default=0)),
                ('propagate', models.IntegerField(default=0, choices=[(0, b'NOT PROPAGATED'), (2, b'PROPAGATED')])),
                ('channel_datatype', models.CharField(max_length=255, choices=[(b'uint8', b'uint8'), (b'uint16', b'uint16'), (b'uint32', b'uint32'), (b'uint64', b'uint64'), (b'float32', b'float32')])),
                ('readonly', models.IntegerField(default=0, choices=[(1, b'Yes'), (0, b'No')])),
                ('exceptions', models.IntegerField(default=0, choices=[(1, b'Yes'), (0, b'No')])),
                ('startwindow', models.IntegerField(default=0)),
                ('endwindow', models.IntegerField(default=0)),
                ('default', models.BooleanField(default=False)),
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
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
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
                ('host', models.CharField(default=b'localhost', max_length=255, choices=[(b'localhost', b'localhost'), (b'openconnecto.me', b'openconnecto.me'), (b'braingraph1.cs.jhu.edu', b'braingraph1'), (b'braingraph1dev.cs.jhu.edu', b'braingraph1dev'), (b'braingraph2.cs.jhu.edu', b'braingraph2'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063')])),
                ('kvengine', models.CharField(default=b'MySQL', max_length=255, choices=[(b'MySQL', b'MySQL'), (b'Cassandra', b'Cassandra'), (b'Riak', b'Riak')])),
                ('kvserver', models.CharField(default=b'localhost', max_length=255, choices=[(b'localhost', b'localhost'), (b'openconnecto.me', b'openconnecto.me'), (b'braingraph1.cs.jhu.edu', b'braingraph1'), (b'braingraph1dev.cs.jhu.edu', b'braingraph1dev'), (b'braingraph2.cs.jhu.edu', b'braingraph2'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063')])),
                ('ocp_version', models.CharField(default=b'0.6', max_length=255)),
                ('schema_version', models.CharField(default=b'0.6', max_length=255)),
                ('dataset', models.ForeignKey(to='ocpuser.Dataset')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
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
                ('project', models.ForeignKey(to='ocpuser.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'db_table': 'tokens',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='channel',
            name='project',
            field=models.ForeignKey(to='ocpuser.Project', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='channel',
            unique_together=set([('project', 'channel_name')]),
        ),
    ]
