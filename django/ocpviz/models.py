# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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
from django.conf import settings
# Each VizProject has some metadata and is comprised of VizLayers
# TODO add a VizDataView which aggregates VizProjects(?)

class VizLayer ( models.Model ):
  layer_name = models.CharField(max_length=255)
  layer_description = models.CharField(max_length=255)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
  
  SERVER_CHOICES = (
        ('localhost', 'localhost'),
        ('brainviz1.cs.jhu.edu', 'brainviz1'),
        ('openconnecto.me', 'openconnecto.me'),
        ('braingraph1.cs.jhu.edu', 'braingraph1'),
        ('braingraph1dev.cs.jhu.edu', 'braingraph1dev'),
        ('braingraph2.cs.jhu.edu', 'braingraph2'),
        ('dsp061.pha.jhu.edu', 'dsp061'),
        ('dsp062.pha.jhu.edu', 'dsp062'),
        ('dsp063.pha.jhu.edu', 'dsp063'),
        )  
  server = models.CharField(max_length=255, choices=SERVER_CHOICES, default="localhost")
  
  LAYER_CHOICES = (
    ('image', 'IMAGES'),
    ('annotation', 'ANNOTATIONS'),
    ('probmap', 'PROBABILITY_MAP'),
    ('rgb', 'RGB'),
    ('timeseries','TIMESERIES'),
  )
  layertype = models.CharField(max_length=255, choices=LAYER_CHOICES)
  token = models.CharField(max_length=255)
  channel = models.CharField(max_length=255)
  # do we want to use the tilecache or ocpcatmaid? (default ocpcatmaid)  
  tilecache = models.BooleanField(default=False) 
  # for mcfc cutout 
  COLOR_CHOICES = (
      ('C', 'cyan'),
      ('M', 'magenta'),
      ('Y', 'yellow'),
      ('R', 'red'),
      ('G', 'green'),
      ('B', 'blue'), 
  )
  color = models.CharField(max_length=255, choices=COLOR_CHOICES, blank=True)

  def __unicode__(self):
    return self.layer_name 

class VizProject ( models.Model ):
  project_name = models.CharField(max_length=255, primary_key=True, verbose_name="Name for this visualization project.")
  project_description = models.CharField(max_length=4096, blank=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
  # AB TODO if private, require login 
  PUBLIC_CHOICES = (
      (1, 'Yes'),
      (0, 'No'),
  )
  public = models.IntegerField(choices=PUBLIC_CHOICES, default=0)
  
  layers = models.ManyToManyField(VizLayer, related_name='project')


  xoffset = models.IntegerField(default=0)
  ximagesize = models.IntegerField()
  yoffset = models.IntegerField(default=0)
  yimagesize = models.IntegerField()
  zoffset = models.IntegerField(default=0)
  zimagesize = models.IntegerField()

  starttime = models.IntegerField(default=0)
  endtime = models.IntegerField(default=0)

  minres = models.IntegerField(default=0)
  scalinglevels = models.IntegerField()

  def __unicode__(self):
    return self.project_name
   
class DataViewItem ( models.Model ):
  name = models.CharField(max_length=255, verbose_name="An item attached to a particular dataview.")
  desc_int = models.CharField(max_length=255, verbose_name="An internal description for this item. The external description will be the project description.")
  user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
  
  # link to the vizproject 
  vizproject = models.ForeignKey(VizLayer)
 
  # optional fields to allow a user to define a different starting position 
  xstart = models.IntegerField(default=0)
  ystart = models.IntegerField(default=0)
  zstart = models.IntegerField(default=0)

  marker_start = models.BooleanField(default=False)

  thumbnail_img = models.ImageField(upload_to='ocpviz/thumbnails/')  
  thumbnail_url = models.CharField(max_length=255, default='') 

  def __unicode__(self):
    return self.item_name 

class DataView ( models.Model ):
  name = models.CharField(max_length=255, primary_key=True, verbose_name="Long name for this data view.")
  desc = models.CharField(max_length=255)
  token = models.CharField(max_length=255, verbose_name="The identifier / access name for this dataview (appears in ocp/ocpviz/dataview/<<token>>/)")
  user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)

  items = models.ManyToManyField(DataViewItem, related_name='dataview')

  public = models.BooleanField(default=False)

  def __unicode__(self):
    return self.dataview_name

