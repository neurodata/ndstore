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

from __future__ import absolute_import
import os
import sys
from contextlib import closing
import argparse
import csv
sys.path.append(os.path.abspath('../django'))
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from ndingest.settings.settings import Settings
ndingest_settings = Settings.load()
import django
django.setup()
from django.conf import settings
from ndlib.ndctypelib import XYZMorton
from ndcube.cube import Cube
from ndlib.ndtype import *
from ndlib.restutil import *
from ndproj.nddataset import NDDataset
from ndproj.ndchannel import NDChannel
from ndproj.ndproject import NDProject
from ndproj.ndtoken import NDToken
from spdb.spatialdb import SpatialDB
from spdb.s3io import S3IO
from ndingest.nddynamo.cuboidindexdb import CuboidIndexDB
from ndingest.ndbucket.cuboidbucket import CuboidBucket
from ndlib.s3util import generateS3BucketName, generateS3Key


class ResourceInterface():

  def __init__(self, dataset_name, project_name, token_name, host_name):
    self.dataset_name = dataset_name
    self.project_name = project_name
    self.token_name = token_name
    self.host = host_name

  def createDataset(self):
    dataset = NDDataset.fromName(self.dataset_name)
    try:
      response = getJson('http://{}/resource/dataset/{}/'.format(self.host, self.dataset_name))
      if response.status_code == 404:
        response = postJson('http://{}/resource/dataset/'.format(self.host), dataset)
        if response.status_code != 201:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      elif (response.status_code == 200) and (self.dataset_name == response.json()['dataset_name']):
        print "Dataset already exists. Skipping Dataset creation"
      else:
        raise ValueError('The server returned status code {} and content {}'.format(response.status_code, response.json()))
    except Exception as e:
      print (e)
      sys.exit(0)

  def createProject(self):
    project = NDProject.fromName(self.project_name)
    try:
      response = getJson('http://{}/resource/dataset/{}/project/{}/'.format(self.host, self.dataset_name, self.project_name))
      if response.status_code == 404:
        response = postJson('http://{}/resource/dataset/{}/project/'.format(self.host, self.dataset_name), project)
        if response.status_code != 201:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      elif (response.status_code == 200) and (self.project_name == response.json()['project_name']):
        print "Project already exists. Skipping Project creation"
      else:
        raise ValueError('The server returned status code {} and content {}'.format(response.status_code, response.json()))
    except Exception as e:
      print (e)
      sys.exit(0)
  
  def createChannel(self, channel_name):
    project = NDProject.fromName(self.project_name)
    channel = project.getChannelObj(channel_name)
    try:
      response = getJson('http://{}/resource/dataset/{}/project/{}/channel/{}/'.format(self.host, self.dataset_name, self.project_name, channel_name))
      if response.status_code == 404:
        response = postJson('http://{}/resource/dataset/{}/project/{}/channel/'.format(self.host, self.dataset_name, self.project_name), channel)
        if response.status_code != 201:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      elif (response.status_code == 200) and (channel_name == response.json()['channel_name']):
        print "Channel already exists. Skipping Channel creation"
      else:
        raise ValueError('The server returned status code {} and content {}'.format(response.status_code, response.json()))
    except Exception as e:
      print (e)
      sys.exit(0)
    
  def createToken(self):
    token = NDToken.fromName(self.token_name)
    try:
      response = getJson('http://{}/resource/dataset/{}/project/{}/token/{}/'.format(self.host, self.dataset_name, self.project_name, self.token_name))
      if response.status_code == 404:
        response = postJson('http://{}/resource/datset/{}/project/{}/token/'.format(self.host, self.dataset_name, self.project_name), token)
        if response.status_code != 201:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      elif (response.status_code == 200) and (self.token_name == response.json()['token_name']):
        print "Token already exists. Skipping Token creation"
      else:
        raise ValueError('The server returned status code {} and content {}'.format(response.status_code, response.json()))
    except Exception as e:
      print (e)
      sys.exit(0)
  
    def deleteDataset(self):
      try:
        response = deleteJson('http://{}/resource/dataset/{}/'.format(self.host, self.dataset_name))
        if response.status_code != 204:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      except Exception as e:
        print (e)
    
    def deleteProject(self):
      try:
        response = deleteJson('http://{}/resource/dataset/{}/project/{}'.format(self.host, self.dataset_name, self.project_name))
        if response.status_code != 204:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      except Exception as e:
        print (e)
    
    def deleteChannel(self, channel_name):
      try:
        response = deleteJson('http://{}/resource/dataset/{}/project/{}/channel/{}'.format(self.host, self.dataset_name, self.project_name, channel_name))
        if response.status_code != 204:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      except Exception as e:
        print (e)

    def deleteToken(self):
      try:
        response = deleteJson('http://{}/resource/dataset/{}/project/{}/token/{}'.format(self.host, self.dataset_name, self.project_name, self.token_name))
        if response.status_code != 204:
          raise ValueError('The server returned status code {}'.format(response.status_code))
      except Exception as e:
        print (e)


class AwsInterface:

  def __init__(self, token, host_name):
    """Create the bucket and intialize values"""
  
    self.token = token
    self.proj = NDProject.fromTokenName(self.token)
    self.resource_interface = ResourceInterface(self.proj.dataset_name, self.proj.project_name, self.token, host_name)
    
    with closing (SpatialDB(self.proj)) as self.db:
      # create the s3 I/O and index objects
      self.s3_io = S3IO(self.db)
      self.cuboid_bucket = CuboidBucket(self.proj.project_name)
      self.cuboidindex_db = CuboidIndexDB(self.proj.project_name)
      # self.file_type = result.file_type
      # self.tile_size = result.tile_size
      # self.data_location = result.data_location
      # self.url = result.url
  
  def deleteToken(self):
    """Delete the Token"""
    
    self.resource_interface.deleteToken()
    print 'Delete successful for token {}'.format(self.token)

  def deleteProject(self):
    """Delete the project"""

    for item in self.cuboidindex_db.queryProjectItems():
      self.cuboid_bucket.deleteObject(item['supercuboid_key'])
      self.cuboidindex_db.deleteItem(item['supercuboid_key'])
    self.resource_interface.deleteToken()
    self.resource_interface.deleteProject()
    print 'Delete successful for project {}'.format(self.proj.project_name)
  
  
  def deleteChannel(self, channel_name):
    """Delete the channel"""

    for item in self.cuboidindex_db.queryChannelItems():
      self.cuboid_bucket.deleteObject(item['supercuboid_key'])
      self.cuboidindex_db.deleteItem(item['supercuboid_key'])
    self.resource_interface.deleteChannel(channel_name)
    print 'Delete successful for channel {}'.format(channel_name)


  def deleteResolution(self, channel_name, resolution):
    """Delete an existing resolution"""
    
    for item in self.cuboidindex_db.queryResolutionItems(channel_name, resolution):
      self.cuboid_bucket.deleteObject(item['supercuboid_key'])
      self.cuboidindex_db.deleteItem(item['supercuboid_key'])
    print 'Delete successful for resolution {} for channel {}'.format(resolution, channel_name)

  
  def setupNewProject(self):
    """Setup a new project if it does not exist"""
    
    self.resource_interface.createDataset()
    self.resource_interface.createProject()
    self.resource_interface.createToken()

  def uploadExistingProject(self, channel_name, resolution):
    """Upload an existing project to S3"""
      
    self.setupNewProject()
    db = SpatialDB(self.proj)
    # checking for channels
    if channel_name is None:
      channel_list = None
    else:
      channel_list = [channel_name]
    
    # iterating over channels in a project
    for ch in self.proj.projectChannels(channel_list):
      
      # creating the channel resource
      self.resource_interface.createChannel(ch.channel_name)
      # ingest 1 or more resolutions based on user input
      if resolution is None:
        start_res = self.proj.datasetcfg.scalinglevels
        stop_res = ch.resolution - 1
      else:
        start_res = resolution
        stop_res = resolution - 1
      
      # iterating over resolution
      for cur_res in range(start_res, stop_res, -1):
        
        # get the source database sizes
        [image_size, time_range] = self.proj.datasetcfg.dataset_dim(cur_res)
        [xcubedim, ycubedim, zcubedim] = cubedim = self.proj.datasetcfg.get_cubedim(cur_res)
        offset = self.proj.datasetcfg.get_offset(cur_res)
        [xsupercubedim, ysupercubedim, zsupercubedim] = supercubedim = self.proj.datasetcfg.get_supercubedim(cur_res)
        # set the limits for iteration on the number of cubes in each dimension
        [xlimit, ylimit, zlimit] = limit = self.proj.datasetcfg.get_supercube_limit(cur_res)

        for z in range(xlimit):
          for y in range(ylimit):
            for x in range(zlimit):

              try:
                # cutout the data at the current resolution
                data = db.cutout(ch, [x*xsupercubedim, y*ysupercubedim, z*zsupercubedim], [xsupercubedim, ysupercubedim, zsupercubedim], cur_res).data
                # generate the morton index
                morton_index = XYZMorton([x, y, z])

                print "Inserting Cube {} at res {}".format(morton_index, cur_res), [x,y,z]
                # updating the index
                # self.cuboidindex_db.putItem(ch.channel_name, cur_res, x, y, z)
                # inserting the cube
                # self.s3_io.putCube(ch, cur_res, morton_index, blosc.pack_array(data))
              
              except Exception as e:
                # checkpoint the ingest
                self.checkpoint_ingest(ch.channel_name, cur_res, x, y, z, e)
                raise e
  

  def checkpoint_ingest(self, channel_name, resolution, x, y, z, e, time=0):
    """Checkpoint the progress to file"""
    
    with closing(open('checkpoint_ingest.csv', 'wb')) as csv_file:
      field_names = ['project_name', 'channel_name', 'resolution', 'x', 'y', 'z', 'time', 'exception']
      csv_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=field_names)
      csv_writer.writeheader()
      csv_writer.writerow({'project_name' : self.proj.project_name, 'channel_name' : channel_name, 'resolution' : resolution, 'x' : x, 'y' : y, 'z' : z, 'time' : time, 'exception' : e.message})

  
  def load_checkpoint(self):
    """Load from a checkpoint file"""
    return NotImplemented

def main():
  
  parser = argparse.ArgumentParser(description="Upload an existing project of NeuroData to s3")
  parser.add_argument('token', action='store', help='Token for the project')
  parser.add_argument('--channel', dest='channel_name', action='store', type=str, default=None, help='Channel Name in the project')
  parser.add_argument('--res', dest='resolution', action='store', type=int, default=None, help='Resolution to upload')
  parser.add_argument('--action', dest='action', action='store', choices=['upload', 'delete-channel', 'delete-res', 'delete-project'], default='upload', help='Specify action for the given project')
  parser.add_argument('--host', dest='host_name', action='store', type=str, default='localhost:8000', help='Server host name')
  # Unwanted field which might be useful in the future
  # parser.add_argument('--file', dest='file_type', action='store', choices=['tif', 'tiff', 'jpg', 'png'], default='tif', help='File type')
  # parser.add_argument('--new', dest='new_project', action='store', choices=['slice', 'catmaid'], default='slice', help='New Project')
  # parser.add_argument('--tilesz', dest='tile_size', action='store', type=int, default=512, help='Tile Size')
  # parser.add_argument('--data', dest='data_location', action='store', type=str, default='/data/scratch/', help='File Location')
  # parser.add_argument('--url', dest='url', action='store', type=str, help='Http URL')
  result = parser.parse_args()
  
  aws_interface = AwsInterface(result.token, result.host_name)
  if result.action == 'upload':
    if result.channel_name is None and result.resolution is not None:
      raise ValueError("Error: channel cannot be empty if resolution is not empty")
    aws_interface.uploadExistingProject(result.channel_name, result.resolution)
  elif result.action == 'delete-project':
    aws_interface.deleteProject()
  elif result.action == 'delete-channel':
    if result.channel_name is None:
      raise ValueError("Error: channel cannot be empty")
    aws_interface.deleteChannel(result.channel_name)
  elif result.action == 'delete-res':
    if result.channel_name is None or result.resolution is None:
      raise ValueError("Error: channel or resolution cannot be empty")
    aws_interface.deleteResolution(result.channel_name, result.resolution)
  else:
    raise ValueError("Error: Invalid action {}".format(result.action))


if __name__ == '__main__':
  main()
