# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0004_auto_20150415_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vizproject',
            name='layers',
            field=models.ManyToManyField(related_name='project', to='ocpviz.VizLayer'),
            preserve_default=True,
        ),
    ]
