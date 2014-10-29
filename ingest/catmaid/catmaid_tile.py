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
import cStringIO
import numpy as np
from PIL import Image
import zlib

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import zindex
import ocpcarest
import ocpcaproj
import ocpcadb


class CatmaidIngest:

  def __init__( self, token, resolution, tilesz, tilepath ):
    """Load the CATMAID stack into an OCP database"""

    # Get the database
    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.db = ocpcadb.OCPCADB ( self.proj )
    self.tilesz = tilesz
    self.tilepath = tilepath
    self.resolution = resolution

  def ingest ( self ):
    """Read the stack and ingest"""

    # for all specified resolutions

    print "Building DB for resolution ", self.resolution, " imagesize ", self.proj.datasetcfg.imagesz[self.resolution]
    # load a database
    #[ db, proj, projdb ] = ocpcarest.loadDBProj ( self.token )
    
    (startslice, endslice) = self.proj.datasetcfg.slicerange
    (xcubedim, ycubedim, zcubedim) = self.proj.datasetcfg.cubedim[self.resolution]
    (ximagesz, yimagesz) = self.proj.datasetcfg.imagesz[self.resolution]
    batchsz = zcubedim

    numxtiles = ximagesz / self.tilesz
    numytiles = yimagesz / self.tilesz

    # Ingest in database aligned slabs in the z dimension
    for sl in range( startslice, endslice, batchsz ):

      # over all tiles in that slice
      for ytile in range( numytiles ):
        for xtile in range( numxtiles ):

          # RBTODO need to generalize to other project types
          slab = np.zeros ( [zcubedim, self.tilesz, self.tilesz], dtype=np.uint8 )

          # over each slice
          for b in range( batchsz ):

            #if we are at the end of the space, quit
            if ( sl + b <= endslice ):
            
              filename = '{}z{:0>4}/c{:0>2}r{:0>2}.tif'.format(self.tilepath, sl+b, ytile+1, xtile+1 )
              print filename
              try:
                # add tile to stack
                img = Image.open ( filename, 'r' )
                slab [b,:,:] = np.asarray ( img )
              except IOError, e:
                print "Failed to open file %s" % (e)
                img = np.zeros((self.tilesz,self.tilesz), dtype=np.uint8)
                slab [b,:,:] = img


          for y in range ( ytile*self.tilesz, (ytile+1)*self.tilesz, ycubedim ):
            for x in range ( xtile*self.tilesz, (xtile+1)*self.tilesz, xcubedim ):

              mortonidx = zindex.XYZMorton ( [ x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
              cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint8 )

              xmin = x % self.tilesz
              ymin = y % self.tilesz
              xmax = ( min(ximagesz-1, x+xcubedim-1)%self.tilesz ) + 1
              ymax = ( min(yimagesz-1, y+ycubedim-1)%self.tilesz ) + 1
              zmin = 0
              zmax = min(sl+zcubedim,endslice)

              cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax,ymin:ymax,xmin:xmax]

              # create the DB BLOB
              fileobj = cStringIO.StringIO ()
              np.save ( fileobj, cubedata )
              cdz = zlib.compress (fileobj.getvalue())
              
              # insert the blob into the database
              cursor = self.db.conn.cursor()
              sql = "INSERT INTO res{} (zindex, cube) VALUES (%s, %s)".format(int(self.resolution))
              cursor.execute(sql, (mortonidx, cdz))
              cursor.close()

            print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl)
          self.db.conn.commit()


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

