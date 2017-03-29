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
import numpy as np
import blosc
import argparse
sys.path.append(os.path.abspath('../django'))
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from ndingest.nddynamo.cuboidindexdb import CuboidIndexDB
from ndingest.ndbucket.cuboidbucket import CuboidBucket
from ndlib.restutil import *
from ndlib.ndctypelib import *
from scripts_helper import *
import logging
HOST_NAME = 'localhost:8080'

class S3Cuboid(object):

  def __init__(self, project_name, host_name=HOST_NAME):
    # configuring the logger based on the dataset we are uploading
    self.logger = logging.getLogger(project_name)
    self.logger.setLevel(logging.INFO)
    fh = logging.FileHandler('{}_upload.log'.format(project_name))
    self.logger.addHandler(fh)

    self.cuboidindex_db = CuboidIndexDB(project_name)
    self.cuboid_bucket = CuboidBucket(project_name)
    self.info = JsonInfo(host_name, project_name)

  def upload(self, file_name, project_name, channel_name, resolution, x_index, y_index, z_index, time_index=0, neariso=False):
    """Upload a 4D supercuboid directly to dynamo and s3"""
    with open(file_name) as file_handle:
      super_zidx = XYZMorton(x_index, y_index, z_index)
      self.logger.info("Inserting cube {},{},{}".format(x_index, y_index, z_index))
      self.cuboidindex_db.putItem(channel_name, resolution, x_index, y_index, z_index, time_index, neariso=neariso)
      self.cuboid_bucket.putObject(channel_name, resolution, super_zidx, time_index, blosc.pack_array(file_handle.read()), neariso=neariso)


def main():

  parser = argparse.ArgumentParser(description="Upload a supercuboid to S3")
  parser.add_argument('file_name', action='store', type=str, help='File Name')
  parser.add_argument('project_name', action='store', type=str, help='Project Name')
  parser.add_argument('channel_name', action='store', type=str, help='Channel Name')
  parser.add_argument('resolution', action='store', type=int, help='Resolution')
  parser.add_argument('indexes', action='store', type=int, nargs=3, metavar=('X', 'Y', 'Z'), default=[0, 0, 0], help='X, Y, Z co-ordinates of the supercuboid')
  parser.add_argument('--time', dest='time_index', action='store', type=int, default=0, help='Time index')
  parser.add_argument('--neariso', dest='neariso', action='store', type=bool, default=False, help='Neariso')
  parser.add_argument('--host', dest='host_name', action='store', type=str, default=HOST_NAME, help='Server host name')
  parser.add_argument('--supercube', dest='super_cube', action='store_true', default=False, help='Return supercube dimension')
  result = parser.parse_args()
  
  s3_cuboid = S3Cuboid(result.project_name, result.host_name)
  if result.super_cube:
    print (s3_cuboid.info.supercuboid_dimension(result.resolution))
  else:
    s3_cuboid.upload(result.file_name, result.project_name, result.channel_name, result.resolution, result.indexes[0], result.indexes[1], result.indexes[2], result.time_index, result.neariso)

if __name__ == '__main__':
  main()
