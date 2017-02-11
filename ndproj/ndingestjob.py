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

from django.core.exceptions import ObjectDoesNotExist
from autoingest.models import IngestJob
from ndproj.ndobject import NDObject
from ndproj.nddataset import NDDataset
from ndproj.ndproject import NDProject
from ndproj.ndchannel import NDChannel

class NDIngestJob(NDObject):

  def __init__(self, ingest_job):

    self._job = ingest_job

  @classmethod
  def fromJson(cls, ingest_job):
    job = IngestJob(**cls.deserialize(ingest_job))
    return cls(job)
  
  @classmethod
  def fromId(cls, job_id):
    try:
      job = IngestJob.objects.get(id = job_id)
      return cls(job)
    except ObjectDoesNotExist as e:
      raise

  def save(self):
    try:
      self._job.save()
    except Exception as e:
      raise

  def create(self):
    try:
      self.save()
    except Exception as e:
      raise

  def delete(self):
    try:
      self._job.delete()
    except Exception as e:
      raise

  @property
  def upload_queue(self):
    return self._job.upload_queue
  
  @upload_queue.setter
  def upload_queue(self, value):
    self._job.upload_queue = value

  @property
  def ingest_queue(self):
    return self._job.ingest_queue
  
  @ingest_queue.setter
  def ingest_queue(self, value):
    self._job.ingest_queue = value

  @property
  def cleanupqueue(self):
    return self._job.cleanupqueue

  @cleanupqueue.setter
  def cleanupqueue(self, value):
    self._job.cleanupqueue = value

  @property
  def status(self):
    return self._job.status
  
  @status.setter
  def status(self, value):
    self._job.status = value

  @property
  def dataset(self):
    return self._job.dataset
    # return NDDataset.fromName(self._job.dataset)
  
  @dataset.setter
  def dataset(self, value):
    self._job.dataset = value

  @property
  def project(self):
    return self._job.project
    # return NDProject.fromName(self._job.project)
  
  @project.setter
  def project(self, value):
    self._job.project = value

  @property
  def channel(self):
    return self._job.channel
    # proj = NDProject.fromName(self._job.project)
    # return proj.getChannelObj(self._job.channel)

  @channel.setter
  def channel(self):
    self._job.channel = value

  @property
  def resolution(self):
    return self._job.resolution

  @property
  def x_start(self):
    return self._job.x_start

  @property
  def y_start(self):
    return self._job.y_start

  @property
  def z_start(self):
    return self._job.z_start

  @property
  def t_start(self):
    return self._job.t_start
  
  @property
  def x_stop(self):
    return self._job.x_stop

  @property
  def y_stop(self):
    return self._job.y_stop

  @property
  def z_stop(self):
    return self._job.z_stop

  @property
  def t_stop(self):
    return self._job.t_stop
  
  @property
  def tile_size_x(self):
    return self._job.tile_size_x

  @property
  def tile_size_y(self):
    return self._job.tile_size_y

  @property
  def tile_size_z(self):
    return self._job.tile_size_z
  
  @property
  def user_id(self):
    return self._job.user_id

  @user_id.setter
  def user_id(self, value):
    self._job.user_id = value
