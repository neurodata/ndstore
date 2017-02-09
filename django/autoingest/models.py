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
from django.conf import settings
from ndlib.ndtype import *

class IngestJob(models.Model):
  
  user = models.ForeignKey(settings.AUTH_USER_MODEL)
  start_date = models.DateTimeField(auto_now_add=True)
  end_date = models.DateTimeField(null=True)
  upload_queue = models.URLField(max_length=512, null=True)
  ingest_queue = models.URLField(max_length=512, null=True)
  cleanup_queue = models.URLField(max_length=512, null=True)
  INGEST_STATUS_OPTIONS = (
      (INGEST_STATUS_PREPARING, 'Preparing'),
      (INGEST_STATUS_UPLOADING, 'Uploading'),
      (INGEST_STATUS_COMPLETE, 'Complete'),
      (INGEST_STATUS_DELETED, 'Deleted'),
  )
  status = models.IntegerField(choices=INGEST_STATUS_OPTIONS, default=INGEST_STATUS_PREPARING)
  dataset = models.CharField(max_length=128)
  project = models.CharField(max_length=128)
  channel = models.CharField(max_length=128)
  resolution = models.IntegerField()
  file_type = models.CharField(max_length=128)
  x_start = models.IntegerField()
  y_start = models.IntegerField()
  z_start = models.IntegerField()
  t_start = models.IntegerField()
  x_stop = models.IntegerField()
  y_stop = models.IntegerField()
  z_stop = models.IntegerField()
  t_stop = models.IntegerField()
  tile_size_x = models.IntegerField()
  tile_size_y = models.IntegerField()
  tile_size_z = models.IntegerField()
  tile_size_t = models.IntegerField()

  class Meta:
    db_table = "ingest_job"
    managed = True

  def __unicode__(self):
    return '{}'.format(self.id)
