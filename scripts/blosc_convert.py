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

import argparse
import sys
import os
import numpy as np
import h5py
import tempfile
import urllib, urllib2
import cStringIO
from PIL import Image
import zlib
import MySQLdb
#from cassandra.cluster import Cluster

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
import django
from django.conf import settings
django.setup()

from ndproj import NDProjectsDB
from spatialdb import SpatialDB
from ndctypelib import XYZMorton


def main():
  
  parser = argparse.ArgumentParser(description='Convert a database from NPZ to blosc')
  parser.add_argument('token', action="store", type=str, help='Token for the project')
  parser.add_argument('channel_name', action="store", type=str, help='Channel Name for the project')
  parser.add_argument('output_name', action="store", type=str, help='Output Channel Name for the project')
  parser.add_argument('res', action="store", type=int, help='Resolution for the project')
  result = parser.parse_args()

  proj = NDProjectsDB.loadToken(result.token)
  ch = proj.getChannelObj(result.channel_name)
  out_ch = proj.getChannelObj(result.output_name)
  db = SpatialDB(proj)

  # Get the dataset configuration
  [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(result.res)
  [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[result.res]
  [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[result.res]

  # Set the limits for iteration on the number of cubes in each dimension
  xlimit = (ximagesz-1) / xcubedim + 1
  ylimit = (yimagesz-1) / ycubedim + 1
  zlimit = (zimagesz-1) / zcubedim + 1
  
  for z in range(0, zlimit+1, 1):
    for y in range(0, ylimit+1, 1):
      for x in range(0, xlimit+1, 1):
        
        # print x*xcubedim, ":", y*ycubedim, ":", z*zcubedim
        zidx = XYZMorton([x,y,z])
        try:
          db.NPZ = True
          cube = db.getCube(ch, zidx, result.res)
        
          if cube.isNotZeros():
            db.NPZ = False
            print "Ingesting {},{},{}".format(x,y,z)
            db.putCube(out_ch, zidx, result.res, cube, update=False)
        except Exception as e:
          pass


if __name__ == "__main__":
  main()
