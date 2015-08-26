# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0005_auto_20150415_2128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vizproject',
            name='layers',
        ),
        migrations.AddField(
            model_name='vizlayer',
            name='project',
            field=models.ForeignKey(related_name='layer', blank=True, to='ocpviz.VizProject', null=True),
            preserve_default=True,
        ),
    ]
