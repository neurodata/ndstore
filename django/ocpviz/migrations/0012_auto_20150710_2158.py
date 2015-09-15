# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0011_vizlayer_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizproject',
            name='endtime',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vizproject',
            name='starttime',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
