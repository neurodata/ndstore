# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vizproject',
            old_name='secondary_layers',
            new_name='layers',
        ),
        migrations.RemoveField(
            model_name='vizproject',
            name='primary_layer',
        ),
        migrations.AddField(
            model_name='vizlayer',
            name='required',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
