# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0002_auto_20150708_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='NIFTIHeader',
            fields=[
                ('channel', models.ForeignKey(primary_key=True, serialize=False, to='ocpuser.Channel')),
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
            name='header',
            field=models.CharField(default=b'', max_length=8192, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='host',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063'), (b'localhost', b'localhost')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='kvserver',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063')]),
        ),
    ]
