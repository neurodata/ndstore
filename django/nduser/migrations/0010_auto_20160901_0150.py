# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 05:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0009_merge_20160823_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='s3backend',
            field=models.IntegerField(choices=[(1, b'Yes'), (0, b'No')], default=1),
        ),
    ]
