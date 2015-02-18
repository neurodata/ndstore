# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class Dataset ( models.Model):
    dataset = models. CharField(max_length=200, unique=True,verbose_name="Name of the Image dataset")    
    ximagesize =  models.IntegerField()
    yimagesize =  models.IntegerField()

    startslice = models.IntegerField()
    endslice = models.IntegerField()
    startwindow = models.IntegerField(default=0)
    endwindow = models.IntegerField(default=0)
    starttime = models.IntegerField(default=0)
    endtime = models.IntegerField(default=0)
    zoomlevels = models.IntegerField()
    zscale = models.FloatField()
    description  =  models. CharField(max_length=4096)
    
    class Meta:
        """ Meta """
        db_table = u"datasets"
        managed = True
       
    def __unicode__(self):
        return self.dataset


class Project ( models.Model):
    project_name  =  models. CharField(max_length=200, primary_key=True)
    project_description  =  models. CharField(max_length=4096, blank=True)
    #user = models.ForeignKey(settings.AUTH_USER_MODEL)
    dataset  =  models.ForeignKey(Dataset)

    DATATYPE_CHOICES = (
        (1, 'IMAGES'),
        (2, 'ANNOTATIONS'),
        (3, 'CHANNEL_16bit'),
        (4, 'CHANNEL_8bit'),
        (5, 'PROBMAP_32bit'),
        (6, 'BITMASK'),
        (7, 'ANNOTATIONS_64bit'),
        (8, 'IMAGES_16bit'),
        (9, 'RGB_32bit'),
        (10, 'RGB_64bit'),
        (11,'TIMESERIES_4d_8bit'),
        (12,'TIMESERIES_4d_16bit'),
        )
    datatype = models.IntegerField(choices=DATATYPE_CHOICES, default=1)
    #    dataurl  =  models. CharField(max_length=200)
    overlayproject = models. CharField(max_length=200,default="None")
    OVERLAY_SERVER_CHOICES = (
        ('openconnecto.me', 'openconnecto.me'),
        ('braingraph1.cs.jhu.edu', 'braingraph1.cs.jhu.edu'),
        ('braingraph1dev.cs.jhu.edu', 'braingraph1dev'),
        ('braingraph2.cs.jhu.edu', 'braingraph2'),
        ('dsp061.pha.jhu.edu', 'dsp061'),
        ('dsp062.pha.jhu.edu', 'dsp062'),
        ('dsp063.pha.jhu.edu', 'dsp063'),
        
    )
    overlayserver =  models.CharField(max_length=200, choices=OVERLAY_SERVER_CHOICES, default='openconnecto.me')
    
    resolution = models.IntegerField(default=0)

    EXCEPTION_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    exceptions =  models.IntegerField(choices=EXCEPTION_CHOICES, default=2)
    HOST_CHOICES = (
        ('localhost', 'localhost'),
        ('openconnecto.me', 'openconnecto.me'),
        ('braingraph1.cs.jhu.edu', 'braingraph1'),
        ('braingraph1dev.cs.jhu.edu', 'braingraph1dev'),
        ('braingraph2.cs.jhu.edu', 'braingraph2'),
        ('dsp061.pha.jhu.edu', 'dsp061'),
        ('dsp062.pha.jhu.edu', 'dsp062'),
        ('dsp063.pha.jhu.edu', 'dsp063'),

        )
    host =  models.CharField(max_length=200, choices=HOST_CHOICES, default='localhost')
    
    KVENGINE_CHOICES = (
        ('MySQL','MySQL'),
        ('Cassandra','Cassandra'),
        ('Riak','Riak'),

        )
    kvengine =  models.CharField(max_length=255, choices=KVENGINE_CHOICES, default='MySQL')
    KVSERVER_CHOICES = (
        ('localhost','localhost'),
        ('172.23.253.61','dsp061'),
        ('172.23.253.62','dsp062'),
        ('172.23.253.63','dsp063'),
        )
    kvserver =  models.CharField(max_length=255, choices=KVSERVER_CHOICES, default='localhost')

    PROPAGATE_CHOICES = (
        (0, 'NOT PROPAGATED'),
        (1, 'UNDER PROPAGATION'),
        (2, 'PROPAGATED'),
        )
    propagate =  models.IntegerField(choices=PROPAGATE_CHOICES, default=0)


    class Meta:
        """ Meta """
        db_table = u"projects"
        managed = True

        
    def __unicode__(self):
        return self.project_name


class Token ( models.Model):
    token_name  =  models. CharField(max_length=200, primary_key=True)
    token_description  =  models. CharField(max_length=4096,blank=True)
    project  = models.ForeignKey(Project)
    READONLY_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    readonly =  models.IntegerField(choices=READONLY_CHOICES, default=2)
    PUBLIC_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    public =  models.IntegerField(choices=PUBLIC_CHOICES, default=2)
    
    
    class Meta:
        """ Meta """
         # Required to override the default table name
        db_table = u"tokens"
        managed = True
    def __unicode__(self):
        return self.token_name
