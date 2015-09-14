# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0010_auto_20150504_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizlayer',
            name='color',
            field=models.CharField(blank=True, max_length=255, choices=[(b'C', b'cyan'), (b'M', b'magenta'), (b'Y', b'yellow'), (b'R', b'red'), (b'G', b'green'), (b'B', b'blue')]),
            preserve_default=True,
        ),
    ]
