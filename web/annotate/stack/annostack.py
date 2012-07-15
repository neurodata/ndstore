import argparse
import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO

import empaths
import annproj
import anndb
import dbconfig
import zindex

from ann_cy import addData

"""Construct an annotation hierarchy off of a completed annotation database."""

class AnnoStack:
  """Stack of annotations."""

  def __init__(self, token):
    """Load the annotation database and project"""

    annprojdb = annproj.AnnotateProjectsDB()
    self.annoproj = annprojdb.getAnnoProj ( token )
    self.dbcfg = dbconfig.switchDataset ( self.annoproj.getDataset() )

    # Bind the annotation database
    self.annoDB = anndb.AnnotateDB ( self.dbcfg, self.annoproj )


  def createTables ( self  ):
    """Create the database tables""" 
    pass

  def store ( self, level ):
    """Write the current cube to the database at this level"""
    pass


  def buildStack ( self, startlevel ):
    """Build the hierarchy of annotations"""

    for  l in range ( startlevel, len(self.dbcfg.resolutions)-1 ):

      # Get the source database sizes
      [ximagesz, yimagesz] = self.dbcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = self.dbcfg.cubedim [ l ]

      # Get the slices
      [ startslice, endslice ] = self.dbcfg.slicerange
      slices = endslice - startslice + 1

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      #  Round up the zlimit to the next larger
      zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

      # These constants work for all resolutions.  Bigger batches are harder.
      #  They require logic about 
      #  They also transfer entire blocks. 
      # Create an output buffer
      outdata = np.zeros ( [ zcubedim*4, ycubedim*2, xcubedim*2 ] )

      # We've written to this offset already
      prevmortonidx = 0

      # Round up to the top of the range
      lastzindex = (zindex.XYZMorton([xlimit,ylimit,zlimit])/64+1)*64

      # Iterate over the cubes in morton order
      for mortonidx in range(0, lastzindex, 64): 

        print "Working on batch %s at %s" % (mortonidx, zindex.MortonXYZ(mortonidx))
        
        # call the range query
        self.annoDB.queryRange ( mortonidx, mortonidx+64, l );

        # Flag to indicate no data.  No update query
        somedata = False

        # get the first cube
        [key,cube]  = self.annoDB.getNextCube ()

        #  if there's a cube, there's data
        if key != None:
          somedata = True

        while key != None:

          xyz = zindex.MortonXYZ ( key )

          # Compute the offset in the output data cube 
          #  we are placing 4x4x4 input blocks into a 2x2x4 cube 
          offset = [(xyz[0]%4)*(xcubedim/2), (xyz[1]%4)*(ycubedim/2), (xyz[2]%4)*zcubedim]

          print "res : zindex = ", l, ":", key, ", location", zindex.MortonXYZ(key)

          # add the contribution of the cube in the hierarchy
          #self.addData ( cube, outdata, offset )
          # use the cython version
          addData ( cube, outdata, offset )

          # Get the next value
          [key,cube]  = self.annoDB.getNextCube ()

        # Now store the data 
        if somedata == True:

          #  Get the base location of this batch
          xyzout = zindex.MortonXYZ ( mortonidx )

          outcorner = [ xyzout[0]/2*xcubedim, xyzout[1]/2*ycubedim, xyzout[2]*zcubedim ]

          #  Data stored in z,y,x order dims in x,y,z
          outdim = [ outdata.shape[2], outdata.shape[1], outdata.shape[0]]

          # Preserve annotations made at the specified level RBTODO fix me
          self.annoDB.annotateDense ( outcorner, l+1, outdata, 'O' )
            
          # zero the output buffer
          outdata = np.zeros ([zcubedim*4, ycubedim*2, xcubedim*2])

        else:
          print "No data in this batch"


def main():

  parser = argparse.ArgumentParser(description='Build a stack of annotations')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", type=int, help='Start (highest) resolution')
  
  result = parser.parse_args()

  # Create the annotation stack
  annstack = AnnoStack ( result.token )

  # Iterate over the database creating the hierarchy
  annstack.buildStack ( result.resolution )
  



if __name__ == "__main__":
  main()

