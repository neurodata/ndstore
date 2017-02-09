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
import argparse
import cStringIO
import numpy as np
from PIL import Image
import zlib
from contextlib import closing

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import imagecube
import ndlib
import ocpcarest
import ocpcaproj
import ocpcadb


class CatmaidIngest:

  def __init__( self, token, resolution, tilesz, tilepath ):
    """Load the CATMAID stack into an OCP database"""

    self.token = token
    self.tilesz = tilesz
    self.tilepath = tilepath
    self.resolution = resolution

  def ingest ( self ):
    """Read the stack and ingest"""

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      proj = projdb.loadProject ( self.token )

    with closing ( ocpcadb.OCPCADB (proj) ) as db:

      (startslice, endslice) = proj.datasetcfg.slicerange
      (xcubedim, ycubedim, zcubedim) = cubedims = proj.datasetcfg.cubedim[self.resolution]
      (ximagesz, yimagesz) = proj.datasetcfg.imagesz[self.resolution]
      batchsz = zcubedim

      numxtiles = ximagesz / self.tilesz
      numytiles = yimagesz / self.tilesz 

      # Ingest in database aligned slabs in the z dimension
      for sl in range( startslice, endslice, batchsz ):

        # over all tiles in that slice
        for ytile in range( 0, numytiles ):
          for xtile in range( 0, numxtiles ):

            slab = np.zeros ( [zcubedim, self.tilesz, self.tilesz], dtype=np.uint8 )

            # over each slice
            for b in range( batchsz ):

              #if we are at the end of the space, quit
              if ( sl + b <= endslice ):
              
                filename = '{}z{:0>4}/c{:0>2}r{:0>2}.tif'.format(self.tilepath, sl+b, xtile+1, ytile+1 )
                #filename = '{}{}/c{:0>3}r{:0>3}.jpg'.format(self.tilepath, sl+b, xtile, ytile )
                #filename = '{}{}/{}_{}_{}.jpg'.format(self.tilepath, sl+b, ytile, xtile, self.resolution )
                #filename = '{}{}/{}/{}_{}.jpg'.format(self.tilepath, sl+b, self.resolution, ytile, xtile )
                #filename = '{}z{:0>4}/c{:0>2}r{:0>2}.tif'.format(self.tilepath, sl+b, ytile+1, xtile+1 )
                print filename
                try:
                  # add tile to stack
                  img = Image.open ( filename, 'r' )
                  slab [b,:,:] = np.asarray ( img )[:,:,0]
                except IOError, e:
                  print "Failed to open file %s" % (e)
                  img = np.zeros((self.tilesz,self.tilesz), dtype=np.uint8)
                  slab [b,:,:] = img


            for y in range ( ytile*self.tilesz, (ytile+1)*self.tilesz, ycubedim ):
              for x in range ( xtile*self.tilesz, (xtile+1)*self.tilesz, xcubedim ):

                zidx = ndlib.XYZMorton ( [ x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
                cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint8 )

                xmin = x % self.tilesz
                ymin = y % self.tilesz
                xmax = ( min(ximagesz-1, x+xcubedim-1)%self.tilesz ) + 1
                ymax = ( min(yimagesz-1, y+ycubedim-1)%self.tilesz ) + 1
                zmin = 0
                zmax = min(sl+zcubedim,endslice)

                cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax,ymin:ymax,xmin:xmax]
                cube = imagecube.ImageCube16 ( cubedims )
                cube.data = cubedata
                if np.count_nonzero ( cube.data ) != 0:
                  db.putCube ( zidx, self.resolution, cube )

              print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl)
            db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a CATMAID stack')
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int)
  parser.add_argument('tilesz', action="store", type=int)
  parser.add_argument('tilepath', action="store")

  result = parser.parse_args()

  ci = CatmaidIngest ( result.token, result.resolution, result.tilesz, result.tilepath )
  ci.ingest()


if __name__ == "__main__":
  main()

