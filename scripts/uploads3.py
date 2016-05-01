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
import s3io
from s3util import generateS3BucketName, generateS3Key

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class S3Uploader:

  def __init__(self, result):
    """Create the bucket and intialize values"""
  
    self.token = result.token
    self.channel_name = result.channel_name
    self.resolution = result.resolution
    self.proj = ndproj.NDProjectsDB.loadToken(self.token)
    self.db = spatialdb.SpatialDB(self.proj)
    self.file_type = result.file_type
    self.tile_size = result.tile_size
    self.data_location = result.data_location
    self.url = result.url
    try:
      self.client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    except Exception, e:
      logger.error("Cannot connect to S3 backend")
      raise NDWSError("Cannot connect to S3 backend")
    
    # setting up the world
    # self.createS3Bucket()

    # calling the coorect upload method
    if result.new_project == 'slice':
      self.uploadSliceProject()
    elif result.new_project == 'catmaid':
      self.uploadCatmaidProject()
    else:
      self.uploadExistingProject()
   
  def generateCatmaidFileName(self, slice_number, xtile, ytile, ondisk=True):
    """Generate a file name given the slice_number"""
    
    if ondisk:
      return '{}_{}_{}.{}'.format(slice_number, ytile, xtile, self.file_type)
    else:
      return '{}_{}.{}'.format(ytile, xtile, self.file_type)
  
  def fetchCatmaidData(self, slice_list, xtile, ytile):
    """Fetch the next set of data from a remote source and place it locally"""
    
    import pdb; pdb.set_trace()
    # iterating over the slice number list
    for slice_number in slice_list:
      # generating the url based on some parameters
      url = '{}/{}/{}/{}/{}/{}'.format(self.url, 'hildebrand16', self.channel_name, slice_number, self.resolution, self.generateCatmaidFileName(slice_number, xtile, ytile, ondisk=False))
      
      # fetching the object
      try:
        data = self.client.get_object(Bucket='', Key='').get('Body').read()
      except Exception, e:
        logger.warning("Cannot find s3 object {}".format())
        continue
        
      # writing the file to scratch
      try:
        catmaid_file = open('{}'.format(self.data_location+self.generateCatmaidFileName(slice_number, xtile, ytile)),'w')
        catmaid_file.write(data)
      except IOError, e:
        logger.warning("IOError. Could not open file {}. {}".format(self.data_location+self.generateCatmaidFileName(slice_number, xtile, ytile), e))
      finally:
        catmaid_file.close()

  def cleanCatmaidData(self, slice_list, xtile, ytile):
    """Remove the slices at the local store"""

    for slice_number in slice_list:
      try:
        os.remove('{}{}'.format(self.data_location, self.generateCatmaidFileName(slice_number, xtile, ytile)))
      except OSError, e:
        logger.warning("File {} not found. {}".format(self.generateCatmaidFileName(slice_number, xtile, ytile), e))

  def createS3Bucket(self, project_name):
    """Create s s3 bucket"""
    
    # Creating a resource, similar to a client
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(generateS3BucketName(project_name))
    
    # Creating a bucket
    try:
      logger.warning("Creating bucket {}.".format(generateS3BucketName(project_name)))
      bucket.create()
    except Exception as e:
      logger.error("There was an error in creating the bucket {}.".format(generateS3BucketName(project_name)))
      raise NDWSError("There was an error in creating the bucket {}.".format(generateS3BucketName(project_name)))


  def uploadCatmaidProject(self):
    """Ingest a CATMAID tile stack"""
    
    tilesz = 1024
    # Load a database
    proj = ndproj.NDProjectsDB().loadToken(self.token)
    db = spatialdb.SpatialDB(proj)
    s3db = s3io.S3IO(db)
    ch = proj.getChannelObj(self.channel_name)
    
    # creating bucket
    # self.createS3Bucket(proj.getProjectName())

    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
    [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
    [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]
    [xsupercubedim, ysupercubedim, zsupercubedim] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

    if ch.getChannelType() in TIMESERIES_CHANNELS:
      logger.error("Timeseries data not supported for CATMAID data. Error in {}".format(self.token))
      raise NDWSError("Timeseries data not supported for CATMAID data. Error in {}".format(self.token))
    
    num_xtiles = ximagesz / tilesz
    num_ytiles = yimagesz / tilesz
      
    # over all the tiles in the slice
    for ytile in range(0, num_ytiles, 1):
      for xtile in range(0, num_xtiles, 1):
          
        # Get a list of the files in the directories
        for slice_number in range (zoffset, zimagesz, zsupercubedim):
          # empty slab
          slab = np.zeros([zsupercubedim, tilesz, tilesz], dtype=ND_dtypetonp.get(ch.getDataType()))
          
          # prefetch data
          self.fetchCatmaidData(range(slice_number, slice_number+zsupercubedim) if slice_number+zsupercubedim<=zimagesz else range(slice_number, zimagesz), xtile, ytile)
          
          for b in range(zsupercubedim):
            if (slice_number + b < zimagesz):
              try:
                # reading the raw data
                file_name = "{}{}".format(self.data_location, self.generateCatmaidFileName(slice_number+b, xtile, ytile))
                logger.info("Open filename {}".format(file_name))
                # print "Open filename {}".format(file_name)
                slab[b,:,:] = np.asarray(Image.open(file_name, 'r'))[:,:,0]
              except IOError, e:
                logger.warning("IOError {}.".format(e))
                slab[b,:,:] = np.zeros((tilesz, tilesz), dtype=ND_dtypetonp.get(ch.getDataType()))

          for y in range (ytile*tilesz, (ytile+1)*tilesz, ysupercubedim):
            for x in range (xtile*tilesz, (xtile+1)*tilesz, xsupercubedim):

              # Getting a Cube id and ingesting the data one cube at a time
              zidx = ndlib.XYZMorton ( [(x-xoffset)/xsupercubedim, (y-yoffset)/ysupercubedim, (slice_number-zoffset)/zsupercubedim] )
              cube = Cube.getCube(supercubedim, ch.getChannelType(), ch.getDataType())
              cube.zeros()

              xmin = x % tilesz
              ymin = y % tilesz
              xmax = ( min(ximagesz-xoffset-1, x+xsupercubedim-1) % tilesz ) + 1
              ymax = ( min(yimagesz-yoffset-1, y+ysupercubedim-1) % tilesz ) + 1
              zmin = 0
              zmax = min(slice_number-zoffset+zsupercubedim, zimagesz+1)

              cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
              if cube.isNotZeros():
                s3db.putCube(ch, self.resolution, zidx, cube.toBlosc())
      
          # clean up the slices fetched
          self.cleanCatmaidData(range(slice_number,slice_number+zsupercubedim) if slice_number+zsupercubedim<=zimagesz else range(slice_number,zimagesz), xtile, ytile)
  
  
  # def createS3Bucket(self):
    # """Create a S3 bucket"""
    
    # # Creating a resource, similar to a client
    # s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    # bucket = s3.Bucket(generateS3BucketName(self.proj.getProjectName()))
    # # Creating a bucket
    # try:
      # print "Creating bucket"
      # # bucket.create()
    # except Exception as e:
      # logger.error("Bucket {} already exists".format(generateS3BucketName(self.proj.getProjectName())))
      # raise NDWSError("Bucket {} already exists".format(generateS3BucketName(self.proj.getProjectName())))

  # def uploadCatmaidProject(self):
    # """Upload a new catmaid project to S3"""
    
    # ch = self.proj.getChannelObj(self.channel_name)

    # # get the dataset configuration
    # [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = self.proj.datasetcfg.imageSize(self.res)
    # [xcubedim,ycubedim,zcubedim] = cubedim = self.proj.datasetcfg.getCubeDims()[self.res]
    # [xoffset, yoffset, zoffset] = self.proj.datasetcfg.getOffset()[self.res]
    # [xsupercubedim, ysupercubedim, zsupercubedim ] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

    # if ch.getChannelType() in TIMESERIES_CHANNELS:
      # logger.error("Timeseries Data not supported for CATMAID format. Error in {}".format(self.token))
      # raise NDWSError("Timeseries Data not supported for CATMAID format. Error in {}".format(self.token))
    
    # num_xtiles = ximagesz / self.tile_size
    # num_ytiles = yimagesz / self.tile_size

    # # Get a list of the files in the directories
    # for slice_number in range (zoffset, zimagesz, zcubedim):
      
      # # over all the tiles in the slice
      # for ytile in range(0, num_ytiles):
        # for xtile in range(0, num_xtiles):
      
          # slab = np.zeros([zsupercubedim, self.tile_size, self.tile_size ], dtype=np.uint8)
          
          # for b in range(zsupercubedim):
            # if (slice_number + b < zimagesz):
              # try:
                # # reading the raw data
                # file_name = "{}{}/{}_{}.{}".format(self.data_location, slice_number + b, ytile, xtile, self.file_type)
                # logger.info("Open filename {}".format(file_name))
                # print "Open filename {}".format(file_name)
                # slab[b,:,:] = np.asarray(Image.open(file_name, 'r'))
              # except IOError, e:
                # logger.warning("IOError {}.".format(e))
                # slab[b,:,:] = np.zeros((self.tile_size, self.tile_size), dtype=np.uint32)

          # for y in range (ytile*self.tile_size, (ytile+1)*self.tile_size, ysupercubedim):
            # for x in range (xtile*self.tile_size, (xtile+1)*self.tile_size, xsupercubedim):

              # # Getting a Cube id and ingesting the data one cube at a time
              # zidx = ndlib.XYZMorton ( [(x-xoffset)/xsupercubedim, (y-yoffset)/ysupercubedim, (slice_number-zoffset)/zsupercubedim] )
              # cube = Cube.getCube(supercubedim, ch.getChannelType(), ch.getDataType())
              # cube.zeros()
              
              # xmin = x % self.tile_size
              # ymin = y % self.tile_size
              # xmax = min(ximagesz, x+xsupercubedim)
              # ymax = min(yimagesz, y+ysupercubedim)
              # zmin = 0
              # zmax = min(slice_number-zoffset+zsupercubedim, zimagesz+1)

              # cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
              # if cube.isNotZeros():
                # pass
                # s3io.putCube(ch, cur_res, zidx, blosc.pack_array(data))


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

        [xs, ys, zs ] = supercubedim = map(mul, cubedim, SUPERCUBESIZE)

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
              # m = hashlib.md5()
              # m.update('{}_{}'.format(zidx,cur_res))
              # s3_key = m.hexdigest()
              # generateS3Key(ch.getChannelName(), cur_res, zidx)

              print "Inserting Cube {} at res {}".format(zidx, cur_res), [x,y,z]
              # data = blosc.pack_array(data)
              s3io.putCube(ch, cur_res, zidx, blosc.pack_array(data))
              # Uploading the object to S3
              # bucket.put_object(Key=s3_key, Body=data)

        print "Time for Resolution {} : {} secs".format(cur_res, time.time()-start)

def main():
  
  parser = argparse.ArgumentParser(description="Upload an existing project of OCP to s3")
  parser.add_argument('token', action='store', help='Token for the project')
  parser.add_argument('channel_name', action='store', help='Channel Name in the project')
  parser.add_argument('--res', dest='resolution', action='store', type=int, default=0, help='Resolution to upload')
  parser.add_argument('--file', dest='file_type', action='store', choices=['tif', 'tiff', 'jpg', 'png'], default='tif', help='File type')
  parser.add_argument('--new', dest='new_project', action='store', choices=['slice', 'catmaid'], default='slice', help='New Project')
  parser.add_argument('--tilesz', dest='tile_size', action='store', type=int, default=512, help='Tile Size')
  parser.add_argument('--data', dest='data_location', action='store', type=str, default='/data/scratch/', help='File Location')
  parser.add_argument('--url', dest='url', action='store', type=str, help='Http URL')

  result = parser.parse_args()
  
  start = time.time()
  s3up = S3Uploader(result)
  print "Total Time for Upload: {}".format(time.time()-start)

if __name__ == '__main__':
  main()
