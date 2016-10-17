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

import json
import jsonschema
import django
django.setup()
from django.conf import settings
from ndingest.settings.settings import Settings
ndingest_settings = Settings.load()
from ndlib.ndtype import *
from ndproj.ndproject import NDProject
from ndproj.nddataset import NDDataset
from ndproj.ndchannel import NDChannel
from ndproj.ndingestjob import NDIngestJob
from ndingest.ndingestproj.ndingestproj import NDIngestProj
from ndingest.ndqueue.uploadqueue import UploadQueue
from ndingest.ndqueue.ingestqueue import IngestQueue
from ndingest.ndqueue.cleanupqueue import CleanupQueue
from webservices.ndwserror import NDWSError
from ingest.core.config import Configuration
import logging
logger = logging.getLogger("neurodata")

# KL TODO Load this from settings
TILE_SIZE = 1024


class IngestManager(object):

  def __init__(self):
    # self.ds = None
    # self.pr = None
    # self.ch = None
    self.nd_proj = None
    self.ingest_job = None

  
  def createIngestJob(self, user_id, config_data):
    """Create an ingest job based on the posted config data"""
    
    config_data = json.loads(config_data)
    # validate schema
    if self.validateConfig(config_data):
      try:
        # create the upload queue
        UploadQueue.createQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
        self.ingest_job.upload_queue = UploadQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT).url
        # create the ingest queue
        IngestQueue.createQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
        self.ingest_job.ingest_queue = IngestQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT).url
        # create the cleanup queue
        CleanupQueue.createQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
        self.ingest_job.cleanup_queue = CleanupQueue(self.nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT).url
        # self.generateUploadTasks()
        self.ingest_job.user_id = user_id
        self.ingest_job.save()
        return NDIngestJob.serialize(self.ingest_job._job)

      except Exception as e:
        print (e)
        raise NDWSError(e)


  def validateConfig(self, config_data):
    try:
      ndcg = Configuration(config_data)
      validator = ndcg.get_validator()
      validator.schema = ndcg.schema
      validator.validate_schema()
      ingest_job_json = json.dumps({
          'dataset' : ndcg.config_data["database"]["dataset"],
          'project' : ndcg.config_data["database"]["project"],
          'channel' : ndcg.config_data["database"]["channel"],
          'resolution' : ndcg.config_data["ingest_job"]["resolution"],
          'x_start' : ndcg.config_data["ingest_job"]["extent"]["x"][0],
          'x_stop' : ndcg.config_data["ingest_job"]["extent"]["x"][1],
          'y_start' : ndcg.config_data["ingest_job"]["extent"]["y"][0],
          'y_stop' : ndcg.config_data["ingest_job"]["extent"]["y"][1],
          'z_start' : ndcg.config_data["ingest_job"]["extent"]["z"][0],
          'z_stop' : ndcg.config_data["ingest_job"]["extent"]["z"][1],
          't_start' : ndcg.config_data["ingest_job"]["extent"]["t"][0],
          't_stop' : ndcg.config_data["ingest_job"]["extent"]["t"][1],
          'tile_size_x' : ndcg.config_data["ingest_job"]["tile_size"]["x"],
          'tile_size_y' : ndcg.config_data["ingest_job"]["tile_size"]["y"],
          'tile_size_z' : ndcg.config_data["ingest_job"]["tile_size"]["z"],
          'tile_size_t' : ndcg.config_data["ingest_job"]["tile_size"]["t"],
      })
      self.ingest_job = NDIngestJob.fromJson(ingest_job_json)
      self.nd_proj = NDIngestProj(self.ingest_job.project, self.ingest_job.channel, self.ingest_job.resolution)
    except jsonschema.ValidationError as e:
      raise NDWSError("Schema validation failed")
    except Exception as e:
      return NDWSError("Properties not found")
    return True

  def generateUploadTasks(self):
    """Populate the upload queue with tile names"""
    
    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.dataset_dim(self.resolution)
    # [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
    [xoffset, yoffset, zoffset] = proj.datasetcfg.get_offset(self.resolution)
    # [xsupercubedim, ysupercubedim, zsupercubedim] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

    if ch.channel_type in TIMESERIES_CHANNELS:
      logger.error("Timeseries data not supported for now. Error in {}".format(self.token))
      raise NDWSError("Timeseries data not supported for now. Error in {}".format(self.token))
    
    num_xtiles = ximagesz / TILE_SIZE
    num_ytiles = yimagesz / TILE_SIZE
      
    # over all the tiles in the slice
    for ytile in range(0, num_ytiles, 1):
      for xtile in range(0, num_xtiles, 1):
          
        # Get a list of the files in the directories
        for slice_number in range (zoffset, zimagesz, 1):
          
          # insert message in queue
          print "inserting message:x{}_y{}_z{}".format(xtile, ytile, slice_number)
          self.queue.sendMessage(self.generateFileName(slice_number, xtile, ytile))
  
  def getIngestJob(self, job_id):
    """Get an ingest job based on job id"""
    
    try:
      ingest_job = NDIngestJob.fromId(job_id)
      return NDIngestJob.serialize(ingest_job._job)
    except Exception as e:
      print (e)
      raise
  
  def deleteIngestJob(self, job_id):
    """Delete an ingest job based on job id"""

    try:
      ingest_job = NDIngestJob.fromId(job_id)
      nd_proj = NDIngestProj(ingest_job.project, ingest_job.channel, ingest_job.resolution)
      # delete the upload queue
      UploadQueue.deleteQueue(nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
      # delete the ingest queue
      IngestQueue.deleteQueue(nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
      # delete the cleanup queue
      CleanupQueue.deleteQueue(nd_proj, endpoint_url=ndingest_settings.SQS_ENDPOINT)
      ingest_job.status = INGEST_STATUS_DELETED
      ingest_job.save()
    except Exception as e:
      print (e)
      raise
