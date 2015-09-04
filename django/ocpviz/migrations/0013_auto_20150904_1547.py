# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0012_auto_20150710_2158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vizproject',
            old_name='maxres',
            new_name='scalinglevels',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='xmax',
            new_name='ximagesize',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='xmin',
            new_name='xoffset',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='ymax',
            new_name='yimagesize',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='ymin',
            new_name='yoffset',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='zmax',
            new_name='zimagesize',
        ),
        migrations.RenameField(
            model_name='vizproject',
            old_name='zmin',
            new_name='zoffset',
        ),
        migrations.RemoveField(
            model_name='vizlayer',
            name='required',
        ),
        migrations.AlterField(
            model_name='vizlayer',
            name='channel',
            field=models.CharField(max_length=255),
        ),
    ]
