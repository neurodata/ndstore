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

"""Construct an annotation hierarchy off of a completed annotation database."""


class AnnoStack:
  """Stack of annotations."""

  def __init__(self,token,levels):
    """Load the annotation database and project"""

    annprojdb = annproj.AnnotateProjectsDB()
    self.annoproj = annprojdb.getAnnoProj ( token )
    self.dbcfg = dbconfig.switchDataset ( self.annoproj.getDataset() )
    self._levels = levels
    self._annresolution = self.annoproj.getResolution()

    # Bind the annotation database
    self.annoDB = anndb.AnnotateDB ( self.dbcfg, self.annoproj )


  def createTables ( self  ):
    """Create the database tables""" 
    pass

  def addData ( self, level, cube ):
    """Add the contribution of the cube to this level"""
    pass

  def store ( self, level ):
    """Write the current cube to the database at this level"""
    pass

  def buildLevel ( self, level ):
    """Build a specific level in the hierarcy"""

    # Get the source database sizes
    [src_ximagesz, src_yimagesz] = self.dbcfg.imagesz [ level ]
    [src_xcubedim, src_ycubedim, src_zcubedim] = self.dbcfg.cubedim [ level ]

    # Get the target database sizes
    [trgt_ximagesz, trgt_yimagesz] = self.dbcfg.imagesz [ level + 1 ]
    [trgt_xcubedim, trgt_ycubedim, trgt_zcubedim] = self.dbcfg.cubedim [ level + 2 ]

    # Get the slices
    [ startslice, endslice ] = self.dbcfg.slicerange
    slices = endslice - self.startslice + 1

    # Set the limits for iteration on the number of cubes in each dimension
    xlimit = src_ximagesz / src_xcubedim
    ylimit = src_yimagesz / src_ycubedim
    #  Round up the zlimit to the next larger
    zlimit = (((slices-1)/src_zcubedim+1)*src_zcubedim) * zcubedim

    # Iterate over the cubes in morton order
    for mortonidx in zindex.generator ( [xlimit, ylimit, zlimit] ):
      
      cube = self.annoDB.getCube ( mortonidx )
      
      # add the contribution of the cube in the hierarchy
      # maybe do some batching
        


  def buildStack ( self ):
    """Build the hierarchy of anootations"""

    for  l in range ( self.levels ):

      buildLevel ( l + 1 + self._annresolution )



def main():

  parser = argparse.ArgumentParser(description='Build a stack of annotations')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('levels', action="store", type=int, help='Number of levels in the hierarchy')
  
  result = parser.parse_args()

  # Create the annotation stack
  annstack = AnnoStack ( result.token, result.levels)

  # Iterate over the database creating the hierarchy
  annstack.buildStack ( )
  



if __name__ == "__main__":
  main()

