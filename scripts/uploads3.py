# -*- coding: utf-8 -*-

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

import os
import sys
import boto3
from contextlib import closing
import hashlib
import blosc
import argparse
from operator import add, sub, mul, div, mod
from PIL import Image
import time
import urllib2

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
import django
django.setup()
from django.conf import settings

import ndlib
from cube import Cube
from ndtype import *
import ndproj
import spatialdb
from s3io import S3IO
from nddynamo.s3indexdb import S3IndexDB
from s3util import generateS3BucketName, generateS3Key

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class S3Upload:

  def __init__(self, token, channel_name, resolution):
    """Create the bucket and intialize values"""
  
    self.token = token
    self.channel_name = channel_name
    self.resolution = resolution
    self.proj = ndproj.NDProjectsDB.loadToken(token)
    self.db = spatialdb.SpatialDB(self.proj)
    # self.file_type = result.file_type
    # self.tile_size = result.tile_size
    # self.data_location = result.data_location
    # self.url = result.url
    
  
  def uploadExistingProject(self):
    """Upload an existing project to S3"""

    # Uploading to a bucket

    with closing (ndproj.NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (spatialdb.SpatialDB(proj)) as db:
      
      # create the s3 I/O and index objects
      s3_io = S3IO(db)
      s3index_db = S3IndexDB(proj.getProjectName(), self.channel_name)
      
      # creating the channel obj
      ch = proj.getChannelObj(self.channel_name)
      
      # ingest 1 or more resolutions based on user input
      if self.resolution is None:
        stop_res = ch.getBaseResolution()
        start_res = proj.datasetcfg.scalinglevels
      else:
        start_res = self.resolution
        stop_res = self.resolution - 1
      
      # iterating over resolution
      for cur_res in range(start_res, stop_res, -1):
        
        # get the source database sizes
        [[ximagesz, yimagesz, zimagesz], timerange] = proj.datasetcfg.imageSize(cur_res)
        [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[cur_res]
        [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[cur_res]

        [xs, ys, zs ] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

        # set the limits for iteration on the number of cubes in each dimension
        xlimit = (ximagesz-1) / (xs) + 1
        ylimit = (yimagesz-1) / (ys) + 1
        zlimit = (zimagesz-1) / (zs) + 1

        for z in range(zlimit):
          for y in range(ylimit):
            for x in range(xlimit):

              # cutout the data at the current resolution
              data = db.cutout(ch, [ x*xs, y*ys, z*zs], [xs,ys,zs], cur_res ).data
              zidx = ndlib.XYZMorton ([x,y,z])

              print "Inserting Cube {} at res {}".format(zidx, cur_res), [x,y,z]
              # updating the index
              s3index_db.putItem(cur_res, x, y, z)
              # inserting the cube
              s3_io.putCube(ch, cur_res, zidx, blosc.pack_array(data))


def main():
  
  parser = argparse.ArgumentParser(description="Upload an existing project of NeuroData to s3")
  parser.add_argument('token', action='store', help='Token for the project')
  parser.add_argument('channel_name', action='store', help='Channel Name in the project')
  parser.add_argument('--res', dest='resolution', action='store', type=int, default=None, help='Resolution to upload')
  # parser.add_argument('--file', dest='file_type', action='store', choices=['tif', 'tiff', 'jpg', 'png'], default='tif', help='File type')
  # parser.add_argument('--new', dest='new_project', action='store', choices=['slice', 'catmaid'], default='slice', help='New Project')
  # parser.add_argument('--tilesz', dest='tile_size', action='store', type=int, default=512, help='Tile Size')
  # parser.add_argument('--data', dest='data_location', action='store', type=str, default='/data/scratch/', help='File Location')
  # parser.add_argument('--url', dest='url', action='store', type=str, help='Http URL')
  result = parser.parse_args()
  
  s3_upload = S3Upload(result.token, result.channel_name, result.resolution)
  s3_upload.uploadExistingProject()


if __name__ == '__main__':
  main()
