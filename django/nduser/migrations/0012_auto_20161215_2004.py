# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-16 01:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0011_auto_20161215_0542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='endtime',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='starttime',
        ),
        migrations.AddField(
            model_name='channel',
            name='endtime',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channel',
            name='starttime',
            field=models.IntegerField(default=0),
        ),
    ]
