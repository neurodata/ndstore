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
import numpy as np
import urllib, urllib2
import cStringIO
from contextlib import closing
import csv

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import zindex

"""Extract all points above a threshhold for a specific channel and resolution."""

class ThreshholdStack:

  def __init__(self, token):
    """Load the annotation database and project"""

    projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.annoDB = ocpcadb.OCPCADB ( self.proj )

  def findLocations ( self, channel, resolution, threshhold, outfile ):
    """Build the hierarchy of annotations"""

    # Get the source database sizes
    [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ resolution ]
    [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ resolution ]

    # Get the slices
    [ startslice, endslice ] = self.proj.datasetcfg.slicerange
    slices = endslice - startslice + 1

    # Set the limits for iteration on the number of cubes in each dimension
    xlimit = ximagesz / xcubedim
    ylimit = yimagesz / ycubedim

    #  Round up the zlimit to the next larger
    zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

    # Round up to the top of the range
    lastzindex = (zindex.XYZMorton([xlimit,ylimit,zlimit])/64+1)*64

    locs = []
    
    import pdb; pdb.set_trace()

    with closing (open(outfile, 'wb')) as csvfile:

      # Iterate over the cubes in morton order
      for mortonidx in range(0, lastzindex, 64): 

        print "Working on batch %s at %s" % (mortonidx, zindex.MortonXYZ(mortonidx))
        
        # call the range query
        self.annoDB.queryRange ( mortonidx, mortonidx+64, resolution, channel );

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
          offset = [xyz[0]*xcubedim, xyz[1]*ycubedim, xyz[2]*zcubedim]

          nzlocs = np.nonzero ( cube.data > threshhold )
             
          if len(nzlocs[1]) != 0:

            print "res : zindex = ", resolution , ":", key, ", location", zindex.MortonXYZ(key)
            cubelocs=zip(nzlocs[0],nzlocs[1],nzlocs[2],cb.data[nzlocs[0],nzlocs[1],nzlocs[2]])
            locs = [ (pt[2]+offset[0], pt[1]+offset[1], pt[0]+offset[2], nnzlocs) for pt in cubelocs ] 

            csv.writerows ( [x for x in cubelocs ] )

          [key,cube]  = self.annoDB.getNextCube ()


def main():

  parser = argparse.ArgumentParser(description='Find all points above a threshhold for a specific channel and resolution')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('channel', action="store", help='Channel.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution')
  parser.add_argument('threshhold', action="store", type=int, help='Minimum value')
  parser.add_argument('outfile', action="store")
  
  result = parser.parse_args()

  # Create the annotation stack
  tholder = ThreshholdStack ( result.token, result.outfile )

  # Iterate over the database creating the hierarchy
  tholder.findLocations ( result.channel, result.resolution, result.threshhold )
  



if __name__ == "__main__":
  main()

