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
  
  token = models.CharField(max_length=255)
  channel = models.CharField(max_length=255)
  

class VizProject ( models.Model ):
  project_name = models.CharField(max_length=255, primary_key=True, verbose_name="Name for this visualization project.")
  project_description = models.CharField(max_length=4096, blank=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
  PUBLIC_CHOICES = (
      (1, 'Yes'),
      (0, 'No'),
  )
  public = models.IntegerField(choices=PUBLIC_CHOICES, default=0)
  
  # Primary vizLayer
  primary_layer = models.ForeignKey(VizLayer, related_name="primary_projects")
  # all other layers
  secondary_layers = models.ManyToManyField(VizLayer)
  
  xmin = models.IntegerField(default=0)
  xmax = models.IntegerField()
  ymin = models.IntegerField(default=0)
  ymax = models.IntegerField()
  zmin = models.IntegerField(default=0)
  zmax = models.IntegerField()
 
  minres = models.IntegerField(default=0)
  maxres = models.IntegerField()
    
  
