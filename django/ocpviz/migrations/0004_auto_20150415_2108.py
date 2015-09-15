# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0003_vizlayer_server'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vizlayer',
            name='channel',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
