import argparse
import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO
from PIL import Image
import zlib
import math
import MySQLdb

import empaths
import emcaproj
import emcadb
import zindex

"""Construct an isotropic version of a given resolution"""

class IsoStack:
  """Build an isotropic version of the database at a given resolution."""

  def __init__(self, token):
    """Load the database and project"""

    projdb = emcaproj.EMCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.imgDB = emcadb.EMCADB ( self.proj )


  def buildStack ( self, level ):
    """Build the hierarchy of images"""


    # Get the source database sizes
    [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ level ]
    [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ level ]

    # Get the slices
    [ startslice, endslice ] = self.proj.datasetcfg.slicerange
    slices = endslice - startslice + 1

    # number of slices in isotropic database
    newslices = int(math.floor(slices * self.proj.datasetcfg.zscale[level]))

    # Set the limits for iteration on the number of cubes in each dimension
    # RBTODO These limits may be wrong for even (see channelingest.py)
    xlimit = ximagesz / xcubedim
    ylimit = yimagesz / ycubedim
    #  Round up the zlimit to the next larger
    zlimit = (((newslices-1)/zcubedim+1)*zcubedim)/zcubedim 

    cursor = self.imgDB.conn.cursor()

    for z in range(zlimit):
      for y in range(ylimit):
        self.imgDB.conn.commit()
        for x in range(xlimit):

          # what do we cutout to get the newslices region
          oldzstart = int(math.floor(z*zcubedim/self.proj.datasetcfg.zscale[level]))
          oldzend = int(math.floor((z+1)*zcubedim/self.proj.datasetcfg.zscale[level]))
          #print "oldzstart %s oldzeng %s" % ( oldzstart, oldzend )

          # cutout the data at the -1 resolution
          olddata = self.imgDB.cutout ( [x*xcubedim,y*ycubedim,oldzstart], [xcubedim,ycubedim,oldzend-oldzstart], level ).data
          # target array for the new data (z,y,x) order
          newdata = np.zeros([zcubedim,ycubedim,xcubedim], dtype=np.uint8)

          for sl in range(ycubedim):

            # Convert each slice to an image
            slimage = Image.frombuffer ( 'L', (xcubedim,oldzend-oldzstart), olddata[:,sl,:].flatten(), 'raw', 'L', 0, 1 )

            # Resize the image
            newimage = slimage.resize ( [xcubedim,zcubedim] )
            
            # Put to a new cube
            newdata[:,sl,:] = np.asarray ( newimage )

            # Compress the data
            outfobj = cStringIO.StringIO ()
            np.save ( outfobj, newdata )
            zdataout = zlib.compress (outfobj.getvalue())
            outfobj.close()

          key = zindex.XYZMorton ( [x,y,z] )
          
          # put in the database
          sql = "INSERT INTO res" + str(level) + "iso (zindex, cube) VALUES (%s, %s)"
          print sql % (key,"x,y,z=%s,%s,%s"%(x,y,z))
          try:
            cursor.execute ( sql, (key,zdataout))
          except MySQLdb.Error, e:
            print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

    self.imgDB.conn.commit()

def main():

  parser = argparse.ArgumentParser(description='Build an isotropic version of the database at a given resolution')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution to build')
  
  result = parser.parse_args()

  # Create the annotation stack
  isostack = IsoStack ( result.token )

  # Iterate over the database creating the hierarchy
  isostack.buildStack ( result.resolution )
  


if __name__ == "__main__":
  main()

