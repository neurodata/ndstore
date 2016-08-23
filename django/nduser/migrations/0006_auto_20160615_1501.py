# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nduser', '0005_project_s3backend'),
    ]

    operations = [
        migrations.AddField(
            model_name='histogram',
            name='roi',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='histogram',
            name='region',
            field=models.IntegerField(default=0, choices=[(0, b'Entire Dataset'), (1, b'ROI'), (2, b'RAMON')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='nd_version',
            field=models.CharField(default=b'1.0', max_length=255),
        ),
    ]
