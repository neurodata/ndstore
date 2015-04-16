# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0007_auto_20150415_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vizlayer',
            name='server',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'localhost', b'localhost'), (b'openconnecto.me', b'openconnecto.me'), (b'braingraph1.cs.jhu.edu', b'braingraph1'), (b'braingraph1dev.cs.jhu.edu', b'braingraph1dev'), (b'braingraph2.cs.jhu.edu', b'braingraph2'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063')]),
            preserve_default=True,
        ),
    ]
