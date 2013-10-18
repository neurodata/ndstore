import argparse
import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO
from PIL import Image
import zlib
import MySQLdb

import empaths
import emcaproj
import emcachannel
import emcadb
import zindex

"""Construct an image hierarchy up from a given resolution"""

class ChanStack:
  """Stack of multi-channel images."""

  def __init__(self, token):
    """Load the database and project"""

    projdb = emcaproj.EMCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.chanDB = emcadb.EMCADB ( self.proj )


  def buildStack ( self, startlevel ):
    """Build the hierarchy of images"""

    for  l in range ( startlevel, len(self.proj.datasetcfg.resolutions) ):

      for chnm, chid in self.chanDB.getChannels().iteritems():

        chan = int(chid)

        # Get the source database sizes
        [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ l ]
        [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ l ]

        biggercubedim = [xcubedim*2,ycubedim*2,zcubedim]

        # Get the slices
        [ startslice, endslice ] = self.proj.datasetcfg.slicerange
        slices = endslice - startslice + 1

        # Set the limits for iteration on the number of cubes in each dimension
        # RBTODO These limits may be wrong for even (see channelingest.py)
        xlimit = ximagesz / xcubedim
        ylimit = yimagesz / ycubedim
        #  Round up the zlimit to the next larger
        zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

        cursor = self.chanDB.conn.cursor()

        for z in range(zlimit):
          for y in range(ylimit):
            self.chanDB.conn.commit()
            for x in range(xlimit):

              # cutout the data at the -1 resolution
              olddata = self.chanDB.cutout ( [ x*2*xcubedim, y*2*ycubedim, z*zcubedim ], biggercubedim, l-1, chan ).data
              # target array for the new data (z,y,x) order
              newdata = np.zeros([zcubedim,ycubedim,xcubedim], dtype=np.uint8)

              for sl in range(zcubedim):

                # Convert each slice to an image
                slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'L', 0, 1 )

                # Resize the image
                newimage = slimage.resize ( [xcubedim,ycubedim] )

                # Put to a new cube
                newdata[sl,:,:] = np.asarray ( newimage )
                 
                import pdb; pdb.set_trace()

                # Compress the data
                outfobj = cStringIO.StringIO ()
                np.save ( outfobj, newdata )
                zdataout = zlib.compress (outfobj.getvalue())
                outfobj.close()

              key = zindex.XYZMorton ( [x,y,z] )
              
              # put in the database
              sql = "INSERT INTO res" + str(l) + "(channel, zindex, cube) VALUES (%s, %s, %s)"
              print sql % (chan,key,0)
              try:
                cursor.execute ( sql, (chan,key,zdataout))
              except MySQLdb.Error, e:
                print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

        self.chanDB.conn.commit()

def main():

  parser = argparse.ArgumentParser(description='Build an image stack')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Start (highest) resolution to build')
  
  result = parser.parse_args()

  # Create the annotation stack
  chanstack = ChanStack ( result.token )

  # Iterate over the database creating the hierarchy
  chanstack.buildStack ( result.resolution )
  


if __name__ == "__main__":
  main()

