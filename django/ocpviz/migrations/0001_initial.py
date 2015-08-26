# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VizLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('layer_name', models.CharField(max_length=255)),
                ('layer_description', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('channel', models.CharField(max_length=255)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VizProject',
            fields=[
                ('project_name', models.CharField(max_length=255, serialize=False, verbose_name=b'Name for this visualization project.', primary_key=True)),
                ('project_description', models.CharField(max_length=4096, blank=True)),
                ('public', models.IntegerField(default=0, choices=[(1, b'Yes'), (0, b'No')])),
                ('xmin', models.IntegerField(default=0)),
                ('xmax', models.IntegerField()),
                ('ymin', models.IntegerField(default=0)),
                ('ymax', models.IntegerField()),
                ('zmin', models.IntegerField(default=0)),
                ('zmax', models.IntegerField()),
                ('minres', models.IntegerField(default=0)),
                ('maxres', models.IntegerField()),
                ('primary_layer', models.ForeignKey(related_name='primary_projects', to='ocpviz.VizLayer')),
                ('secondary_layers', models.ManyToManyField(to='ocpviz.VizLayer')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
