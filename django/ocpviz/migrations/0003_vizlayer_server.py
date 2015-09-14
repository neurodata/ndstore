# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0002_auto_20150415_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizlayer',
            name='server',
            field=models.CharField(default=b'localhost', max_length=255),
            preserve_default=True,
        ),
    ]
