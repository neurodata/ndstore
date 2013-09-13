import argparse
import sys
import os

import empaths
import argparse

import emcaproj
import emcadb
 
import numpy as np
from PIL import Image


class CatmaidIngest:

  def __init__( self, token, tilesz, tilepath ):
    """Load the CATMAID stack into an OCP database"""

    # Get the database
    self.projdb = emcaproj.EMCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.db = emcadb.EMCADB ( self.proj )
    self.tilesz = tilesz
    self.prefix=tilepath

  def ingest ( self ):
    """Read the stack and ingest"""

    # for all specified resolutions
    for resolution in reversed(self.proj.datasetcfg.resolutions):

      print "Building DB for resolution ", resolution, " imagesize ", self.proj.datasetcfg.imagesz[resolution]

      zstart = self.proj.datasetcfg.slicerange[0]
      zend = self.proj.datasetcfg.slicerange[1]
      # slices per ingest group
      zslices = self.proj.datasetcfg.cubedim[resolution][2]

      # extract parameters for iteration
      numxtiles = self.proj.datasetcfg.imagesz[resolution][0]/self.tilesz
      numytiles = self.proj.datasetcfg.imagesz[resolution][1]/self.tilesz
      numzslabs = (zend-zstart+1)/zslices + 1


      # Ingest in database aligned slabs in the z dimension
      for zslab in range(numzslabs):

        # over all tiles in that slice
        for ytile in range(numytiles):
          for xtile in range(numxtiles):

            # RBTODO need to generalize to other project types
            cuboid = np.zeros ( [zslices,self.tilesz,self.tilesz], dtype=np.uint8 )

            # over each slice
            for zslice in range(zslices):

              #if we are at the end of the space, quit
              if zslab*zslices+zstart+zslice > zend:
                break
              filename = '{}/{}/{}/{}/{}.jpg'.format(self.prefix,resolution,zslab*zslices+zslice+zstart,ytile,xtile)
              print filename
              try:
                # add tile to stack
                tileimage = Image.open ( filename, 'r' )
                cuboid [zslice,:,:] = np.asarray ( tileimage )
              except IOError, e:
                print "Failed to open file %s" % (e) 
                raise

            # here we have continuous cuboid, let's upload it to the database
            corner = [ xtile*self.tilesz, ytile*self.tilesz, zslab*zslices ]
            self.db.writeImageCuboid ( corner, resolution, cuboid) 
            self.db.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a CATMAID stack')
  parser.add_argument('token', action="store")
  parser.add_argument('tilesz', action="store", type=int)
  parser.add_argument('tilepath', action="store")

  result = parser.parse_args()

  ci = CatmaidIngest ( result.token, result.tilesz, result.tilepath )
  ci.ingest()



if __name__ == "__main__":
  main()

