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

import argparse
import sys
import os
from contextlib import closing

import numpy as np
from PIL import Image
import cStringIO
import zlib
import libtiff
import tifffile

sys.path.append(os.path.abspath('../../django'))
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

from cube import Cube
import ocpcarest
import ocpcadb
import ocpcaproj
import ocplib


def main():

  parser = argparse.ArgumentParser(description='Ingest the TIFF data')
  parser.add_argument('token', action="store", type=str, help='Token for the project')
  parser.add_argument('channel', action="store", type=str, help='Channel for the project')
  parser.add_argument('path', action="store", type=str, help='Directory with the image files')
  parser.add_argument('resolution', action="store", type=int, help='Resolution of data')

  result = parser.parse_args()
  
  # Load a database
  with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
    proj = projdb.loadToken(result.token)

  with closing (ocpcadb.OCPCADB(proj)) as db:

    ch = proj.getChannelObj(result.channel)
    # get the dataset configuration
    [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(result.resolution)
    [xcubedim,ycubedim,zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[result.resolution]
    [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[result.resolution]

    file_name = "{}".format(result.path)
    tif_file = tifffile.imread(file_name)
    slice_number = 0
    # Get a list of the files in the directories
    
    for iteration_number in range(starttime, endtime):
      
      slab = np.zeros([zcubedim, yimagesz, ximagesz], dtype=np.uint16)
      import pdb; pdb.set_trace()  
      slab[slice_number,:,:] = tif_file[iteration_number,:,:]

      for y in range ( 0, yimagesz+1, ycubedim ):
        for x in range ( 0, ximagesz+1, xcubedim ):

          # Getting a Cube id and ingesting the data one cube at a time
          zidx = ocplib.XYZMorton ( [x/xcubedim, y/ycubedim, (slice_number-zoffset)/zcubedim] )
          cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType(), timerange=[0,1])
          cube.zeros()

          xmin = x
          ymin = y
          xmax = min ( ximagesz, x+xcubedim )
          ymax = min ( yimagesz, y+ycubedim )
          zmin = 0
          zmax = min(slice_number+zcubedim, zimagesz+1)

          cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
          db.putTimeCube(ch, zidx, iteration_number, result.resolution, cube, update=False)
            
if __name__ == "__main__":
  main()
