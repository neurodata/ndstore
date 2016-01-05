# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0002_auto_20150923_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='host',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063'), (b'localhost', b'Debug')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='kvserver',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'dsp061.pha.jhu.edu', b'default'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063'), (b'localhost', b'Debug')]),
        ),
    ]
