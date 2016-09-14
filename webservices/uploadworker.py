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

import sys
import os
import urllib
import urllib2
from contextlib import closing
import numpy as np
from PIL import Image
from operator import sub, add, mul, div
import boto3
import botocore
import blosc

import django
django.setup()
from django.conf import settings

from cube import Cube
from ndtype import TIMESERIES_CHANNELS, IMAGE_CHANNELS, ANNOTATION_CHANNELS, ND_dtypetonp, UINT8, UINT16, UINT32, SUPERCUBESIZE
import ndwsrest
import spatialdb
import ndproj
from ndqueue.uploadqueue import UploadQueue

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

# KL TODO Load this from settings
TILE_SIZE = 1024

class UploadWorker:

  def __init__(self, token, channel, resolution, file_type):
    
    self.token = token
    self.channel = channel
    self.resolution = resolution
    # set the file_type
    self.file_type = file_type
    self.queue = UploadQueue()

  def generateFileName(self, slice_number, xtile, ytile):
    """Generate a file name given the slice_number"""
    return '{}_{}_{}.{}'.format(slice_number, ytile, xtile, self.file_type)


  def populateQueue(self):
    """Populate the upload queue with tile names"""
    
    # Load a database
    # with closing (ndproj.NDProjectsDB().loadToken(self.token)) as proj:
      # ch = proj.getChannelObj(self.channel)
    proj = ndproj.NDProjectsDB().loadToken(self.token)
    ch = proj.getChannelObj(self.channel)
    
    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
    # [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
    [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]
    # [xsupercubedim, ysupercubedim, zsupercubedim] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

    if ch.getChannelType() in TIMESERIES_CHANNELS:
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
