# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0004_histogram'),
    ]

    operations = [
        migrations.AddField(
            model_name='histogram',
            name='bins',
            field=models.BinaryField(max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name='histogram',
            name='histogram',
            field=models.BinaryField(max_length=4096, null=True),
        ),
    ]
