# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0007_auto_20160615_1503'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='histogram',
            name='channel',
        ),
        migrations.DeleteModel(
            name='Histogram',
        ),
    ]
