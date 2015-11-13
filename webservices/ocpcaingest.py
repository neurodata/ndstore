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
import urllib
from contextlib import closing
import numpy as np
from PIL import Image
from operator import sub

import django
django.setup()
from django.conf import settings

from cube import Cube
from ndtype import TIMESERIES_CHANNELS, IMAGE_CHANNELS, ANNOTATION_CHANNELS, OCP_dtypetonp, UINT8, UINT16, UINT32
import ocpcarest
import spatialdb
import ocpcaproj
import ndlib

class IngestData:

  def __init__(self, token, channel, resolution, data_url, file_format, file_type):

    self.token = token
    self.channel = channel
    self.resolution = resolution
    self.data_url = data_url
    self.path = settings.TEMP_INGEST_PATH
    # identify which type of data this is
    self.file_format = file_format
    # set the file_type
    self.file_type = file_type

  def ingest(self):
    """Identify the data style and ingest accordingly"""
    
    if self.file_format in ['SLICE']:
      self.ingestImageStack()
    elif self.file_format in ['CATMAID']:
      self.ingestCatmaidStack()
    else:
      raise "Format {} not supported.".format(self.file_format)

  def fetchData(self, slice_list, time_value):
    """Fetch the next set of data from a remote source and place it locally"""
    
    # data is a TIF stack
    for slice_number in slice_list:
      try:
        if time_value is not None:
          url = '{}{}/{}/{}/{}'.format(self.data_url, self.token, self.channel, time_value, self.generateFileName(slice_number))
        else:
          url = '{}{}/{}/{}'.format(self.data_url, self.token, self.channel, self.generateFileName(slice_number))
        urllib.urlretrieve('{}'.format(url), self.path+self.generateFileName(slice_number))
      except Exception, e:
        print "Failed to fetch url {}. File does not exist.".format(url)
 
  def cleanData(self, slice_list):
    """Remove the slices at the local store"""

    for slice_number in slice_list:
      try:
        os.remove('{}{}'.format(self.path, self.generateFileName(slice_number)))
      except OSError:
        print "File {} not found".format(self.generateFileName(slice_number))


  def generateFileName(self, slice_number):
    """Generate a file name given the slice_number"""

    return '{:0>4}.{}'.format(slice_number, self.file_type)

  def ingestCatmaidStack(self):
    """Ingest a CATMAID tile stack"""

    # Load a database
    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing (spatialdb.SPATIALDB(proj)) as db:

      ch = proj.getChannelObj(self.channel)
      # get the dataset configuration
      [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
      [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]

      if ch.getChannelType() in TIMESERIES_CHANNELS and (starttime == 0 and endtime == 0):
        pass
      else:
        print "Timeseries Data cannot have timerange (0,0)"
        raise
      
      num_xtiles = ximagesz / tilesz
      num_ytiles = yimagesz / tilesz

      # Get a list of the files in the directories
      for timestamp in range(starttime, endtime+1):
        for slice_number in range (zoffset, zimagesz+1, zcubedim):
          
          # over all the tiles in the slice
          for ytile in range(0, num_ytiles):
            for xtile in range(o, num_xtiles):
          
              slab = np.zeros([zcubedim, tilesz, tilesz ], dtype=np.uint8)
              for b in range(zcubedim):
                if (slice_number + b <= zimagesz):
                  try:
                    # reading the raw data
                    file_name = "{}{}{:0>6}.{}".format(self.path, self.regex (slice_number + b), self.file_type )
                    print "Open filename {}".format(file_name)
                    slab[b,:,:] = np.asarray(Image.open(file_name, 'r'))
                  except IOError, e:
                    print e
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
                    db.putCube(ch, zidx, self.resolution, cube, update=True)
                  else:
                    db.putTimeCube(ch, zidx, timestamp, self.resolution, cube, update=True)

  def ingestImageStack(self):
    """Ingest a TIF image stack"""

    # Load a database
    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing (spatialdb.SPATIALDB(proj)) as db:

      ch = proj.getChannelObj(self.channel)
      # get the dataset configuration
      [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
      [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]
      
      if ch.getChannelType() in TIMESERIES_CHANNELS and (starttime == 0 and endtime == 0):
        print "Timeseries Data cannot have timerange (0,0)"
        raise

      # Get a list of the files in the directories
      for timestamp in range(starttime, endtime+1):
        for slice_number in range (zoffset, zimagesz+1, zcubedim):
          slab = np.zeros([zcubedim, yimagesz, ximagesz ], dtype=OCP_dtypetonp.get(ch.getDataType()))
          # fetch 16 slices at a time
          if ch.getChannelType() in TIMESERIES_CHANNELS:
            time_value = timestamp
          else:
            time_value = None
          self.fetchData(range(slice_number,slice_number+zcubedim) if slice_number+zcubedim<=zimagesz else range(slice_number,zimagesz), time_value=time_value)
          for b in range(zcubedim):
            if (slice_number + b <= zimagesz):
              try:
                # reading the raw data
                file_name = "{}{}".format(self.path, self.generateFileName(slice_number+b))
                print "Open filename {}".format(file_name)
                if ch.getDataType() in [UINT8, UINT16] and ch.getChannelType() in IMAGE_CHANNELS:
                  image_data = np.asarray(Image.open(file_name, 'r'))
                  slab[b,:,:] = image_data
                elif ch.getDataType() in [UINT32] and ch.getChannelType() in IMAGE_CHANNELS:
                  image_data = np.asarray(Image.open(file_name, 'r').convert('RGBA'))
                  slab[b,:,:] = np.left_shift(image_data[:,:,3], 24, dtype=np.uint32) | np.left_shift(image_data[:,:,2], 16, dtype=np.uint32) | np.left_shift(image_data[:,:,1], 8, dtype=np.uint32) | np.uint32(image_data[:,:,0])
                elif ch.getChannelType() in ANNOTATION_CHANNELS:
                  image_data = np.asarray(Image.open(file_name, 'r'))
                  slab[b,:,:] = image_data
                else:
                  print "Do not ingest this data yet"
                  raise
              except IOError, e:
                print e
                slab[b,:,:] = np.zeros((yimagesz, ximagesz), dtype=np.uint32)
          
          for y in range ( 0, yimagesz+1, ycubedim ):
            for x in range ( 0, ximagesz+1, xcubedim ):

              # Getting a Cube id and ingesting the data one cube at a time
              zidx = ndlib.XYZMorton ( [x/xcubedim, y/ycubedim, (slice_number-zoffset)/zcubedim] )
              cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType())
              cube.zeros()

              xmin,ymin = x,y
              xmax = min ( ximagesz, x+xcubedim )
              ymax = min ( yimagesz, y+ycubedim )
              zmin = 0
              zmax = min(slice_number+zcubedim, zimagesz+1)

              cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
              if cube.isNotZeros():
                if ch.getChannelType() in IMAGE_CHANNELS:
                  db.putCube(ch, zidx, self.resolution, cube, update=True)
                elif ch.getChannelType() in TIMESERIES_CHANNELS:
                  db.putTimeCube(ch, zidx, timestamp, self.resolution, cube, update=True)
                elif ch.getChannelType() in ANNOTATION_CHANNELS:
                  corner = map(sub, [x,y,slice_number], [xoffset,yoffset,zoffset])
                  db.annotateDense(ch, corner, self.resolution, cube.data, 'O')
                else:
                  print "Channel type not supported"
                  raise
          
          # clean up the slices fetched
          self.cleanData(range(slice_number,slice_number+zcubedim) if slice_number+zcubedim<=zimagesz else range(slice_number,zimagesz))

def main():
  """Testing"""

if __name__ == '__main__':
  main()
