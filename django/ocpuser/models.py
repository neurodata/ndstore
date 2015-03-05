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
    dataset_name = models.CharField(max_length=255, primary_key=True,verbose_name="Name of the Image dataset")    
    ximagesize =  models.IntegerField()
    yimagesize =  models.IntegerField()
    zimagesize =  models.IntegerField()
    xoffset =  models.IntegerField(default=0)
    yoffset =  models.IntegerField(default=0)
    zoffset =  models.IntegerField(default=0)
    xvoxelres = models.FloatField(default=1.0)
    yvoxelres = models.FloatField(default=1.0)
    zvoxelres = models.FloatField(default=1.0)

    SCALING_CHOICES = (
        (0, 'Z Slices'),
        (1, 'isotropic'),
        )
    scalingoption = models.IntegerField(default=0, choices=SCALING_CHOICES)
    scalinglevels = models.IntegerField(default=0)
    startwindow = models.IntegerField(default=0)
    endwindow = models.IntegerField(default=0)
    starttime = models.IntegerField(default=0)
    endtime = models.IntegerField(default=0)
    dataset_description = models.CharField(max_length=4096,blank=True)
    
    class Meta:
        """ Meta """
        db_table = u"datasets"
        managed = True
       
    def __unicode__(self):
        return self.dataset_name


class Project ( models.Model):
    project_name  =  models.CharField(max_length=255, primary_key=True)
    project_description  =  models.CharField(max_length=4096, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    dataset = models.ForeignKey(Dataset)

    PROJECT_CHOICES = (
        ('image', 'IMAGES'),
        ('annotation', 'ANNOTATIONS'),
        ('channel', 'CHANNELS'),
        ('probmap', 'PROBABILITY_MAP'),
        ('rgb', 'RGB'),
        ('timeseries','TIMESERIES'),
        )

    DATATYPE_CHOICES = (
        ('uint8', 'uint8'),
        ('uint16', 'uint16'),
        ('uint32', 'uint32'),
        ('uint64', 'uint64'),
        ('float32', 'float32'),
        )


    projecttype = models.CharField(max_length=255,choices=PROJECT_CHOICES,default='image')
    datatype = models.CharField(max_length=255,choices=DATATYPE_CHOICES,default='uint8')
    overlayproject = models.CharField(max_length=255,default="None")
    OVERLAY_SERVER_CHOICES = (
        ('http://openconnecto.me/ocp', 'openconnecto.me'),
        ('http://braingraph1.cs.jhu.edu/ocp', 'braingraph1.cs.jhu.edu'),
        ('http://braingraph1dev.cs.jhu.edu/ocp', 'braingraph1dev'),
        ('http://braingraph2.cs.jhu.edu/ocp', 'braingraph2'),
        ('http://dsp061.pha.jhu.edu/ocp', 'dsp061'),
        ('http://dsp062.pha.jhu.edu/ocp', 'dsp062'),
        ('http://dsp063.pha.jhu.edu/ocp', 'dsp063'),
        ('http://localhost:8000', 'Django dev server'),
        
    )
    overlayserver =  models.CharField(max_length=255, choices=OVERLAY_SERVER_CHOICES, default='openconnecto.me')
    
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
    host =  models.CharField(max_length=255, choices=HOST_CHOICES, default='localhost')
    
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
    token_name = models.CharField(max_length=255, primary_key=True)
    token_description  =  models.CharField(max_length=4096,blank=True)
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
