# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0014_auto_20151007_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataview',
            name='items',
        ),
        migrations.RemoveField(
            model_name='dataview',
            name='user',
        ),
        migrations.RemoveField(
            model_name='dataviewitem',
            name='user',
        ),
        migrations.RemoveField(
            model_name='dataviewitem',
            name='vizproject',
        ),
        migrations.RemoveField(
            model_name='vizlayer',
            name='user',
        ),
        migrations.RemoveField(
            model_name='vizproject',
            name='layers',
        ),
        migrations.RemoveField(
            model_name='vizproject',
            name='user',
        ),
        migrations.DeleteModel(
            name='DataView',
        ),
        migrations.DeleteModel(
            name='DataViewItem',
        ),
        migrations.DeleteModel(
            name='VizLayer',
        ),
        migrations.DeleteModel(
            name='VizProject',
        ),
    ]
