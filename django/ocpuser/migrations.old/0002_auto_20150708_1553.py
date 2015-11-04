# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ocpuser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.CharField(max_length=255, choices=[(b'local', b'file system'), (b's3', b'Amazon S3')])),
                ('description', models.CharField(default=b'', max_length=4096)),
                ('datetimestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Done'), (1, b'Processing'), (2, b'Failed')])),
            ],
            options={
                'db_table': 'backups',
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='channel',
            name='project',
            field=models.ForeignKey(to='ocpuser.Project'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='backup',
            name='channel',
            field=models.ForeignKey(blank=True, to='ocpuser.Channel', null=True),
        ),
        migrations.AddField(
            model_name='backup',
            name='project',
            field=models.ForeignKey(to='ocpuser.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='backup',
            unique_together=set([('project', 'datetimestamp')]),
        ),
    ]
