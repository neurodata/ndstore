# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0008_auto_20160621_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Histogram',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('histogram', models.BinaryField(max_length=4096, null=True)),
                ('bins', models.BinaryField(max_length=4096, null=True)),
                ('region', models.IntegerField(default=0, choices=[(0, b'Entire Dataset'), (1, b'ROI (rectangle)'), (2, b'RAMON')])),
                ('roi', models.TextField(blank=True)),
                ('channel', models.ForeignKey(to='nduser.Channel')),
            ],
            options={
                'db_table': 'histogram',
                'managed': True,
            },
        ),
    ]
