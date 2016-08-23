# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0006_auto_20160615_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='histogram',
            name='region',
            field=models.IntegerField(default=0, choices=[(0, b'Entire Dataset'), (1, b'ROI (rectangle)'), (2, b'RAMON')]),
        ),
    ]
