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

import sys
import os
from contextlib import closing

import numpy as np

import django
django.setup()

from cube import Cube
import ocpcarest
import ocpcadb
import ocpcaproj
import ocplib

class IngestData:

  def __init__(token, channel, resolution, data_url, data_regex):

    self.token = token
    self.channel = channel
    self.resolution = resolution
    self.data_url = data_url
i
  def identifyData():
    """Identify the data"""
    
    # do something with data_regex here to identify
    
    # set the regex and file_type
    self.regex = ""
    self.file_type = ""
    pass

  def fetchData(filename_list):
    """Fetch the next set of data from a remote source and place it locally"""

    # data is a TIF stack
    for file_name in filename_list:
      try:
        urllib.urlretrieve('ftp://{}{}'.format(self.data_url, file_name), file_name)
      except Exception, e:
        print "Failed to fetch url. File does not exist."


  def ingestData():
    """Ingest the data from the local system"""

    # Load a database
    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing (ocpcadb.OCPCADB(proj)) as db:

      ch = proj.getChannelObj(self.channel)
      # get the dataset configuration
      [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
      [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]

      # Get a list of the files in the directories
      for slice_number in range (zoffset, zimagesz+1, zcubedim):
        slab = np.zeros([zcubedim, yimagesz, ximagesz ], dtype=np.uint8)
        for b in range(zcubedim):
          if (slice_number + b <= zimagesz):
            try:
              # reading the raw data
              file_name = "{}{}{:0>6}.{}".format(self.path, self.regex (slice_number + b), self.file_type )
              print "Open filename {}".format(file_name)
              slab[b,:,:] = np.asarray(Image.open(file_name, 'r'))
            except IOError, e:
              print e
              slab[b,:,:] = np.zeros((yimagesz, ximagesz), dtype=np.uint32)

        for y in range ( 0, yimagesz+1, ycubedim ):
          for x in range ( 0, ximagesz+1, xcubedim ):

            # Getting a Cube id and ingesting the data one cube at a time
            zidx = ocplib.XYZMorton ( [x/xcubedim, y/ycubedim, (slice_number-zoffset)/zcubedim] )
            cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType())
            cube.zeros()

            xmin,ymin = x,y
            xmax = min ( ximagesz, x+xcubedim )
            ymax = min ( yimagesz, y+ycubedim )
            zmin = 0
            zmax = min(slice_number+zcubedim, zimagesz+1)

            cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
            if cube.isNotZeros():
              db.putCube(ch, zidx, self.resolution, cube, update=True)
