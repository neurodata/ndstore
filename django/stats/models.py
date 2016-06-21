# Copyright 2014 NeuroData (http://neurodata.io)
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

from nduser.models import Channel

class Histogram (models.Model):
  """ Stores a histogram in npz format """
  channel = models.ForeignKey(Channel)
  histogram = models.BinaryField(max_length=4096, null=True)
  bins = models.BinaryField(max_length=4096, null=True)
  REGION_CHOICES = (
    (0, 'Entire Dataset'),
    (1, 'ROI (rectangle)'), # ROI is a rectangle
    (2, 'RAMON')
  )
  region = models.IntegerField(choices=REGION_CHOICES, default=0)
  roi = models.TextField(blank=True) # stores JSON representation of rectangular ROI

  class Meta:
    db_table = u"histogram"
    managed = True
