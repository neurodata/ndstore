# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0009_auto_20150416_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizlayer',
            name='tilecache',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vizlayer',
            name='layertype',
            field=models.CharField(max_length=255, choices=[(b'image', b'IMAGES'), (b'annotation', b'ANNOTATIONS'), (b'probmap', b'PROBABILITY_MAP'), (b'rgb', b'RGB'), (b'timeseries', b'TIMESERIES')]),
            preserve_default=True,
        ),
    ]
