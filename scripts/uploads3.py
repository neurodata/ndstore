# -*- coding: utf-8 -*-

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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
from django.conf import settings

import django
django.setup()

import ndproj
import spatialdb
import ndlib


class S3Uploader:

  def __init__(self, token, channel_name, res):
    """Create the bucket and intialize values"""
  
    self.token = token
    self.channel_name = channel_name
    self.res = res

  def uploadNewProject(self):
    """Upload a new project to S3"""

    with closing (ndproj.NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (spatialdb.SpatialDB(proj)) as db:
      
      ch = proj.getChannelObj(self.channel_name)

      # KL TODO Add the script for uploading these files directly to the S3 bucket in supercube format

      # Can call ndwsingest

  def uploadExistingProject(self):
    """Upload an existing project to S3"""

    # Uploading to a bucket

    with closing (ndproj.NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (spatialdb.SpatialDB(proj)) as db:

      s3 = boto3.resource('s3')
      bucket = s3.Bucket('{}_{}'.format(proj.getProjectName(), self.channel_name))
      # Creating a bucket
      bucket.create()
      
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
