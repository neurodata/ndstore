# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0003_auto_20151201_2100'),
    ]

    operations = [
        migrations.CreateModel(
            name='Histogram',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('histogram', models.BinaryField(max_length=4096)),
                ('region', models.IntegerField(default=0, choices=[(0, b'Entire Dataset'), (1, b'ROI (AB TODO)')])),
                ('channel', models.ForeignKey(to='ocpuser.Channel')),
            ],
            options={
                'db_table': 'histogram',
                'managed': True,
            },
        ),
    ]
