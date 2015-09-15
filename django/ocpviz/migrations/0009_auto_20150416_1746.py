# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocpviz', '0008_auto_20150415_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='vizlayer',
            name='layertype',
            field=models.CharField(default='Images', max_length=255, choices=[(b'IMAGES', b'Images'), (b'ANNOTATIONS', b'Annotations')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vizlayer',
            name='server',
            field=models.CharField(default=b'localhost', max_length=255, choices=[(b'localhost', b'localhost'), (b'brainviz1.cs.jhu.edu', b'brainviz1'), (b'openconnecto.me', b'openconnecto.me'), (b'braingraph1.cs.jhu.edu', b'braingraph1'), (b'braingraph1dev.cs.jhu.edu', b'braingraph1dev'), (b'braingraph2.cs.jhu.edu', b'braingraph2'), (b'dsp061.pha.jhu.edu', b'dsp061'), (b'dsp062.pha.jhu.edu', b'dsp062'), (b'dsp063.pha.jhu.edu', b'dsp063')]),
            preserve_default=True,
        ),
    ]
