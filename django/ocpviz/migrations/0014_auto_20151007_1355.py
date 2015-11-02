# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ocpviz', '0013_auto_20150904_1547'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataView',
            fields=[
                ('name', models.CharField(max_length=255, serialize=False, verbose_name=b'Long name for this data view.', primary_key=True)),
                ('desc', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255, verbose_name=b'The identifier / access name for this dataview (appears in ocp/ocpviz/dataview/<<token>>/)')),
                ('public', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DataViewItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'An item attached to a particular dataview.')),
                ('desc_int', models.CharField(max_length=255, verbose_name=b'An internal description for this item. The external description will be the project description.')),
                ('xstart', models.IntegerField(default=0)),
                ('ystart', models.IntegerField(default=0)),
                ('zstart', models.IntegerField(default=0)),
                ('marker_start', models.BooleanField(default=False)),
                ('thumbnail_img', models.ImageField(upload_to=b'ocpviz/thumbnails/')),
                ('thumbnail_url', models.CharField(default=b'', max_length=255)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
                ('vizproject', models.ForeignKey(to='ocpviz.VizLayer')),
            ],
        ),
        migrations.AddField(
            model_name='dataview',
            name='items',
            field=models.ManyToManyField(related_name='dataview', to='ocpviz.DataViewItem'),
        ),
        migrations.AddField(
            model_name='dataview',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
