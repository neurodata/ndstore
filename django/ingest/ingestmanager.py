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
import django
django.setup()
from django.conf import settings
from ndtype import *
from ndproj.ndproject import NDProject
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
    self.ds = None
    self.pr = None
    self.ch = None
    self.nd_proj = None
    self.ingest_job = {}

  def createUploadQueue(self):
    UploadQueue.createQueue(self.nd_proj)
    self.ingest_job['upload_queue'] = UploadQueue(self.nd_proj)

  def createIngestQueue(self):
    IngestQueue.createQueue(self.nd_proj)
    self.ingest_job['ingest_queue'] = IngestQueue(self.nd_proj)
  
  def createCleanupQueue(self):
    CleanupQueue.createQueue(self.nd_proj)
    self.ingest_job['cleanup_queue'] = CleanupQueue(self.nd_proj)
  
  def createIngestJob(self, config_data):
    """Create an ingest job based on the posted config data"""

    # validate schema
    if self.validateConfig(config_data):
      try:
        # create the upload queue
        upload_queue = self.createUploadQueue()
        # create the ingest queue
        ingest_queue = self.createIngestQueue()
        # create the cleanup queue
        cleanup_queue = self.createCleanupQueue()
        # self.generateUploadTasks()
        return json.dumps(self.ingest_job)

      except Exception as e:
        print (e)
        raise NDWSError(e)


  def validateConfig(self, config_data):
    try:
      ndcg = Configuration(config_data)
      validator = ndcg.get_validator()
      validator.validate_schema()
      ds = NDDataset(ndcg.config_data["database"]["dataset"])
      pr = NDProject(ndcg.config_data["database"]["project"])
      ch = NDChannel(ndcg.config_data["database"]["channel"])
    except jsonschema.ValidationError as e:
      raise NDWSError("Schema validation failed")
    except Exception as e:
      return NDWSError("Properties not found")
    return True

  def generateUploadTasks(self):
    """Populate the upload queue with tile names"""
    
    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
    # [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
    [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]
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
