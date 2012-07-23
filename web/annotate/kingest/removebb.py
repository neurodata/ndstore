import argparse
import sys
import os

import empaths
import annproj
import dbconfig
import anndb

import zindex

import numpy as np
import cStringIO
import collections
import itertools

import annotation
import anndb
import h5ann

from pprint import pprint

#
#  Remove bounding boxes
#
"""Iterate over the entire database and remove the bounding boxes"""


class BBRemover:
  """Rewrites synapses from old values to separate objects"""

  # lit of identifiers that are bounding boxes
  BBIDS = np.array ([ 2146, 2208, 2216, 2218 ], dtype=np.uint32)

  def __init__(self,token,resolution):
    """DB configuration and some state"""

    self._resolution = resolution

    # Get DB configuration stuff
    annprojdb = annproj.AnnotateProjectsDB()
    annoproj = annprojdb.getAnnoProj ( token )
    self.dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
    self.annodb = anndb.AnnotateDB ( self.dbcfg, annoproj )


  def removeBB ( self ):
    """Iterate over all cubes"""

    # Get the source database sizes
    [ximagesz, yimagesz] = self.dbcfg.imagesz [ self._resolution ]
    [xcubedim, ycubedim, zcubedim] = self.dbcfg.cubedim [ self._resolution ]

    # Get the slices
    [ startslice, endslice ] = self.dbcfg.slicerange
    slices = endslice - startslice + 1

    # Set the limits for iteration on the number of cubes in each dimension
    xlimit = ximagesz / xcubedim
    ylimit = yimagesz / ycubedim
    #  Round up the zlimit to the next larger
    zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim

    lastzindex = (zindex.XYZMorton([xlimit,ylimit,zlimit]))

    # call the range query
#    self.annodb.queryRange ( 0, lastzindex, self._resolution );
    # RB restart
    self.annodb.queryRange ( 0, lastzindex, self._resolution );

    # get the first cube
    [key,cube]  = self.annodb.getNextCube ()

    count = 0 

    while key != None:

      if len (np.intersect1d ( np.unique(cube.data), self.BBIDS )) != 0:
        print "Found bounding box data in cube ", zindex.MortonXYZ( key )
        # Remove annotations
        vector_func = np.vectorize ( lambda a: np.uint32(0) if a in self.BBIDS else a )
        cube.data = vector_func ( cube.data )
        assert(type(cube.data[0,0,0])==np.uint32)
        # Put the cube
        self.annodb.putCube ( key, self._resolution, cube )
        count = count + 1

      else: 
        print "No matching data in ", key

      # Get the next cube
      [key,cube]  = self.annodb.getNextCube ()

      if count == 100:
        self.annodb.conn.commit()
        count = 0

    print "No more cubes"

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution of the ingest data.')
  
  result = parser.parse_args()

  bbr = BBRemover ( result.token, result.resolution )

  bbr.removeBB ()


if __name__ == "__main__":
  main()

