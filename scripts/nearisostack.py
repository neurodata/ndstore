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

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import zindex

"""Construct a near-isotropic version of a given resolution"""

class ZScaleStack:
  """Build a near isotropic version of the database at a given resolution."""
  """keep scaled at integer pixels for use with imglib2"""

  def __init__(self, token):
    """Load the database and project"""

    projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.imgDB = ocpcadb.OCPCADB ( self.proj )


  def buildStack ( self, level ):
    """Build the hierarchy of images"""

    # Get the source database sizes
    [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ level ]
    [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ level ]

    # Get the slices
    [ startslice, endslice ] = self.proj.datasetcfg.slicerange
    slices = endslice - startslice + 1

    # scale by 2 when less than isotropic
    scaling = self.proj.datasetcfg.nearisoscaledown[level]

    # number of slices in isotropic database
    newslices = ((slices-1)/scaling+1)

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


          # cutout the data 
          olddata = self.imgDB.cutout ( [x*xcubedim,y*ycubedim,z*zcubedim*scaling], [xcubedim,ycubedim,zcubedim*scaling], level ).data

          # 3d-averaging
  
          # float64 version 
          oldata_float64 = olddata.astype(np.float64)

          # chunk it into scaling sized slabs          
          chunks=np.array_split(oldata_float64, zcubedim)

          sums = [chunk.sum(0) for chunk in chunks]

          avgs = np.array(sums) / scaling
          # normalize for float to int
          avgs += 0.5
 
          newdata = np.uint8(avgs)

          # Compress the data
          outfobj = cStringIO.StringIO ()
          np.save ( outfobj, newdata )
          zdataout = zlib.compress (outfobj.getvalue())
          outfobj.close()

          key = zindex.XYZMorton ( [x,y,z] )
          
          # put in the database
          sql = "INSERT INTO res" + str(level) + "neariso (zindex, cube) VALUES (%s, %s)"
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
  zscalestack = ZScaleStack ( result.token )

  # Iterate over the database creating the hierarchy
  zscalestack.buildStack ( result.resolution )
  


if __name__ == "__main__":
  main()

