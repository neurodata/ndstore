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
import time

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
import django
django.setup()
from django.conf import settings

import ndlib
from ndtype import *
from ndproj import NDProjectsDB
from spatialdb import SpatialDB
from s3util import generateS3BucketName, generateS3Key

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class S3Uploader:

  def __init__(self, token, channel_name, res, file_type):
    """Create the bucket and intialize values"""
  
    self.token = token
    self.channel_name = channel_name
    self.res = res
    self.proj = NDProjectsDB.loadToken(token)
    self.db = SpatialDB(self.proj)
    self.file_type = file_type
    
    # setting up the world
    self.createS3Bucket()
   

  def createS3Bucket(self):
    """Create a S3 bucket"""
    
    # Creating a resource, similar to a client
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(generateS3BucketName(self.proj.getProjectName()))
    # Creating a bucket
    try:
      bucket.create()
    except Exception as e:
      logger.error("Bucket {} already exists".(generateS3BucketName(self.proj.getProjectName())))
      raise NDWSError("Bucket {} already exists".(generateS3BucketName(self.proj.getProjectName())))

  def uploadCatmaidProject(self):
    """Upload a new catmaid project to S3"""
    
    ch = self.proj.getChannelObj(self.channel_name)

    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = self.proj.datasetcfg.imageSize(self.re)
    [xcubedim,ycubedim,zcubedim] = cubedim = self.proj.datasetcfg.getCubeDims()[self.res]
    [xoffset, yoffset, zoffset] = self.proj.datasetcfg.getOffset()[self.res]

    if ch.getChannelType() in TIMESERIES_CHANNELS:
      logger.error("Timeseries Data not supported for CATMAID format. Error in {}".format(self.token))
      raise NDWSError("Timeseries Data not supported for CATMAID format. Error in {}".format(self.token))
    
    num_xtiles = ximagesz / tilesz
    num_ytiles = yimagesz / tilesz

    # Get a list of the files in the directories
    for slice_number in range (zoffset, zimagesz, zcubedim):
      
      # over all the tiles in the slice
      for ytile in range(0, num_ytiles):
        for xtile in range(0, num_xtiles):
      
          slab = np.zeros([zcubedim, tilesz, tilesz ], dtype=np.uint8)
          
          for b in range(zcubedim):
            if (slice_number + b < zimagesz):
              try:
                # reading the raw data
                file_name = "{}/{}/{}_{}.{}".format(self.path, slice_number + b, ytile, xtile, self.file_type)
                logger.info("Open filename {}".format(file_name))
                print "Open filename {}".format(file_name)
                slab[b,:,:] = np.asarray(Image.open(file_name, 'r'))
              except IOError, e:
                logger.warning("IOError {}.".format(e))
                slab[b,:,:] = np.zeros((tilesz, tilesz), dtype=np.uint32)

          for y in range (ytile*tilesz, (ytile+1)*tilesz, ycubedim):
            for x in range (xtile*tilesz, (xtile+1)*tilesz, xcubedim):

              # Getting a Cube id and ingesting the data one cube at a time
              zidx = ndlib.XYZMorton ( [x/xcubedim, y/ycubedim, (slice_number-zoffset)/zcubedim] )
              cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType())
              cube.zeros()

              xmin = x % tilesz
              ymin = y % tilesz
              xmax = min(ximagesz, x+xcubedim)
              ymax = min(yimagesz, y+ycubedim)
              zmin = 0
              zmax = min(slice_number+zcubedim, zimagesz+1)

              cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
              if cube.isNotZeros():
                s3io.uploadCube(ch, super_zidx, self.res, cube, update=True)


  def uploadSliceProject(self):
    """Upload a new Zslice project to S3"""

    ch = self.proj.getChannelObj(self.channel_name)

    # KL TODO Add the script for uploading these files directly to the S3 bucket in supercube format

    # Cannot call ndwsingest

  def uploadExistingProject(self):
    """Upload an existing project to S3"""

    # Uploading to a bucket

    with closing (ndproj.NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (spatialdb.SpatialDB(proj)) as db:

      
      ch = proj.getChannelObj(self.channel_name)
      
      if self.res == 0:
        start_res = 0
        stop_res = proj.datasetcfg.scalinglevels
      else:
        start_res = self.res
        stop_res = self.res+1
      
      for cur_res in range(start_res, stop_res):
        
        start = time.time()
        # Get the source database sizes
        [[ximagesz, yimagesz, zimagesz], timerange] = proj.datasetcfg.imageSize(cur_res)
        [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[cur_res]
        [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[cur_res]

        [xs, ys, zs ] = supercubedim = [xcubedim*4, ycubedim*4, zcubedim*4]

        # Set the limits for iteration on the number of cubes in each dimension
        xlimit = (ximagesz-1) / (xs) + 1
        ylimit = (yimagesz-1) / (ys) + 1
        zlimit = (zimagesz-1) / (zs) + 1

        for z in range(zlimit):
          for y in range(ylimit):
            for x in range(xlimit):

              # cutout the data at the current resolution
              data = db.cutout(ch, [ x*xs, y*ys, z*zs], [xs,ys,zs], cur_res ).data
              zidx = ndlib.XYZMorton ([x,y,z])
              m = hashlib.md5()
              m.update('{}_{}'.format(zidx,cur_res))
              s3_key = m.hexdigest()

              print "Inserting Cube {} at res {}".format(zidx, cur_res), [x,y,z]
              data = blosc.pack_array(data)
              # Uploading the object to S3
              bucket.put_object(Key=s3_key, Body=data)

        print "Time for Resolution {} : {} secs".format(cur_res, time.time()-start)

def main():
  
  parser = argparse.ArgumentParser(description="Upload an existing project of OCP to s3")
  parser.add_argument('token', action='store', help='Token for the project')
  parser.add_argument('channel_name', action='store', help='Channel Name in the project')
  parser.add_argument('--res', dest='resolution', action='store', type=int, default=0, help='Resolution to upload')
  parser.add_argument('--new', dest='new_project', action='store', type=bool, default=False, help='New Project')

  result = parser.parse_args()
  start = time.time()
  s3up = S3Uploader(result.token, result.channel_name, result.resolution)
  if result.new_project:
    s3up.uploadNewProject()
  else:  
    s3up.uploadExistingProject()
  print "Total Time for Upload: {}".format(time.time()-start)

if __name__ == '__main__':
  main()
