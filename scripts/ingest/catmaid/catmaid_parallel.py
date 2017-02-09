# parallel version of catmaid.py

import argparse
import sys
import os
import pdb

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import multiprocessing

import ocpcaproj
import ocpcadb

import numpy as np
from PIL import Image


def parallel_ingester ( args ):
  """Create an object and run parallel ingest for a zslab."""

  # RB gotta get these from args here.
  token = 'weismX'
  tilesz = 512
  tilepath = '/data3/peeps/wei/DR5_7L_catmaided/'
  reslimit = 1
  resolution = 1

  zslab = args

  ci = CatmaidIngester( token, tilesz, tilepath, reslimit )
  ci.parallelingest ( zslab, resolution )
 

class CatmaidIngester:

  def __init__( self, token, tilesz, tilepath, reslimit ):
    """Load the CATMAID stack into an OCP database"""

    # Get the database
    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.db = ocpcadb.OCPCADB ( self.proj )
    self.tilesz = tilesz
    self.prefix=tilepath
    self.reslimit = reslimit

  def parallelingest(self, zslab, resolution):
   
    # extract parameters for iteration
    numxtiles = self.proj.datasetcfg.imagesz[resolution][0]/self.tilesz
    numytiles = self.proj.datasetcfg.imagesz[resolution][1]/self.tilesz

    zstart = self.proj.datasetcfg.slicerange[0]
    zend = self.proj.datasetcfg.slicerange[1]
    # slices per ingest group
    zslices = self.proj.datasetcfg.cubedim[resolution][2]

    # Ingest in database aligned slabs in the z dimension for each zslab
    
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
          # Writing the missing image-files and not raising an error. Look at missing_files in the same directory 
            f = open('missing_files','a')
            f.write(filename+'\n')
            f.close()
            #raise

        # here we have continuous cuboid, let's upload it to the database
        corner = [ xtile*self.tilesz, ytile*self.tilesz, zslab*zslices ]
        self.db.writeImageCuboid ( corner, resolution, cuboid) 
        self.db.commit()
  

class CatmaidIngest:

  def __init__( self, token, tilesz, tilepath, reslimit, totalprocs ):
    """Load the CATMAID stack into an OCP database"""

    # Get the database
    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.db = ocpcadb.OCPCADB ( self.proj )
    self.tilesz = tilesz
    self.prefix=tilepath
    self.reslimit = reslimit
    self.totalprocs = totalprocs
    self.token = token

  def ingest ( self ):
    """Read the stack and ingest"""

    # for all specified resolutions
    for resolution in reversed(self.proj.datasetcfg.resolutions):

      # Checking for which level of resolution to ingest
      if resolution>self.reslimit:
        continue

      print "Building DB for resolution ", resolution, " imagesize ", self.proj.datasetcfg.imagesz[resolution]

      zstart = self.proj.datasetcfg.slicerange[0]
      zend = self.proj.datasetcfg.slicerange[1]
      # slices per ingest group
      zslices = self.proj.datasetcfg.cubedim[resolution][2]

      numzslabs = (zend-zstart+1)/zslices + 1

      # Building the iterable
      sample_iter = [[self.token, self.tilesz, self.prefix, self.reslimit, resolution]]*numzslabs
      ziterable = zip(sample_iter, range(numzslabs))

      p = multiprocessing.Pool(self.totalprocs)
      p.map ( parallel_ingester, ziterable  )


#  def run( self,numzslabs, zslices, resolution ):
#
#    zslabs = range(numzslabs)
#    ziterable = zip([self]*len(zslabs), zslabs, [resolution]*len(zslabs) )
#
#    pdb.set_trace()
#
#    p = multiprocessing.Pool(self.totalprocs)
#    unwrap_parallel_ingest ( ziterable[0] )
##    p.map(unwrap_parallel_ingest, range(10), 1)
#    p.close()
#    p.join()


def main():

  parser = argparse.ArgumentParser(description='Ingest a CATMAID stack')
  parser.add_argument('token', action="store", help='Token for the project')
  parser.add_argument('tilesz', action="store", type=int, help='Tile size of each jpg image. Mostly 512')
  parser.add_argument('tilepath', action="store", help='Directory with the image files')
  parser.add_argument('processes', action="store", type=int, help='Number of processes',default=4)
  parser.add_argument('--reslimit', action="store", type=int, help='Build upto resolution', default=10) 

  result = parser.parse_args()

  ci = CatmaidIngest ( result.token, result.tilesz, result.tilepath, result.reslimit, result.processes )
  ci.ingest()


if __name__ == "__main__":
  main()
