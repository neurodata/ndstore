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
import argparse
from contextlib import closing
import numpy as np
from PIL import Image

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

import ocpcaproj
import ocpcadb
import ocpcarest
import ocplib
from cube import Cube


class CatmaidIngest:

  def __init__( self, token, channel, resolution, tilesz, tilepath ):
    """Load the CATMAID stack into an OCP database"""

    # Get the database
    self.token = token
    self.channel = channel
    self.resolution = resolution
    self.tilesz = tilesz
    self.tilepath = tilepath

  def ingest ( self ):
    """Read the stack and ingest"""
    
    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (ocpcadb.OCPCADB(proj)) as db:

      ch = proj.getChannelObj(self.channel)
      # get the dataset configuration
      [[ximagesz, yimagesz, zimagesz],(starttime,endtime)] = proj.datasetcfg.imageSize(self.resolution)
      [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]
    
      # for all specified resolutions
      for resolution in range(0,1,1):

        # extract parameters for iteration
        numxtiles = ximagesz/self.tilesz[0]
        numytiles = yimagesz/self.tilesz[1]

        # Ingest in database aligned slabs in the z dimension
        for slice_number in range(0, zimagesz, zcubedim):

          slab = np.zeros ( [zcubedim,yimagesz,ximagesz], dtype=np.uint32 )
          # over all tiles in that slice
          for b in range(zcubedim):
            for ytile in range(numytiles):
              for xtile in range(numxtiles):

                # if we are at the end of the space, quit
                if slice_number+b <= zimagesz:
                  try:
                    filename = '{}{}/{}/{}/{}.png'.format(self.tilepath, resolution, slice_number+b+zoffset, ytile+17, xtile+16)
                    print "Opening filename {}".format(filename)
                    # add tile to stack
                    imgdata = np.asarray ( Image.open(filename, 'r').convert('RGBA') )
                    imgdata = np.left_shift(imgdata[:,:,3], 24, dtype=np.uint32) | np.left_shift(imgdata[:,:,2], 16, dtype=np.uint32) | np.left_shift(imgdata[:,:,1], 8, dtype=np.uint32) | np.uint32(imgdata[:,:,0])
                    slab [b,ytile*self.tilesz[1]:(ytile+1)*self.tilesz[1],xtile*self.tilesz[0]:(xtile+1)*self.tilesz[0]] = imgdata
                  except IOError, e:
                    print "Failed to open file {}".format(filename)
                    slab [b,ytile*self.tilesz[1]:(ytile+1)*self.tilesz[1],xtile*self.tilesz[0]:(xtile+1)*self.tilesz[0]] = np.zeros([self.tilesz[1], self.tilesz[0]], dtype=np.uint32)

          for y in range (0, yimagesz+1, ycubedim):
            for x in range (0, ximagesz+1, xcubedim):
              
              # getting the cube id and ingesting the data one cube at a time
              zidx = ocplib.XYZMorton ([x/xcubedim, y/ycubedim, (slice_number)/zcubedim])
              cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType())
              cube.zeros()

              xmin, ymin = x, y
              xmax = min (ximagesz, x+xcubedim)
              ymax = min (yimagesz, y+ycubedim)
              zmin = 0
              zmax = min(slice_number+zcubedim, zimagesz+1)
              cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
              
              if cube.isNotZeros():
                db.putCube(ch, zidx, self.resolution, cube, update=True)


def main():

  parser = argparse.ArgumentParser(description='Ingest a CATMAID stack')
  parser.add_argument('token', action="store", help='Token for the project')
  parser.add_argument('channel', action="store", help='Channel for the project')
  parser.add_argument('tilepath', action="store")
  parser.add_argument('--resolution', action="store", default=0, type=int, help='Base Resolution')
  parser.add_argument('--tilesz',  nargs=2, type=int, metavar=('X','Y'), action="store", default=[1360,1208], help='Size of the tiles')

  result = parser.parse_args()

  ci = CatmaidIngest ( result.token, result.channel, result.resolution, result.tilesz, result.tilepath )
  ci.ingest()


if __name__ == "__main__":
  main()
