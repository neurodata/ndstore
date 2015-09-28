# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0001_initial'),
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
    ]
