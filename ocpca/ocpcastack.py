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

import sys
import os
import numpy as np
import urllib, urllib2
from contextlib import closing
import cStringIO
import logging

import ocpcaproj
import ocpcadb
import ocplib
from ocpcaerror import OCPCAError

from ocpca_cy import addData_cy

"""Construct an annotation hierarchy off of a completed annotation database."""

class OCPCAStack:
  """Stack of annotations."""

  def __init__ ( self, token ):
    """Load the annotation database and project"""

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as self.projdb:
      self.proj = self.projdb.loadProject ( token )
    

  def buildStack ( self ):
    """ Wrapper for the different datatypes """

    with closing ( ocpcadb.OCPCADB (self.proj) ) as self.db:
      if self.proj.getDBType() in ocpcaproj.ANNOTATION_DATASETS:
        self.buildAnnoStack()
        import pdb; pdb.set_trace()
        self.proj.setPropagate ( ocpcaproj.PROPAGATED )
        self.projdb.updatePropagate ( self.proj )
      else:
        logger.warning("Build function not supported for this datatype")
        raise OCPCAError("Build function not supported for this datatype")

  def buildAnnoStack ( self ):
    """ Build the hierarchy for annotations """
    
    
    for  l in range ( self.proj.datasetcfg.resolutions[0], len(self.proj.datasetcfg.resolutions) ):

      # Get the source database sizes
      [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ l ]

      # Get the slices
      [ startslice, endslice ] = self.proj.datasetcfg.slicerange
      slices = endslice - startslice + 1

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      #  Round up the zlimit to the next larger
      zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

      #  Choose constants that work for all resolutions.
      #   recall that cube size changes from 128x128x16 to 64*64*64
      outdata = np.zeros ( [ zcubedim*4, ycubedim*2, xcubedim*2 ] )

      # Round up to the top of the range
      lastzindex = (ocplib.XYZMorton([xlimit,ylimit,zlimit])/64+1)*64

      # Iterate over the cubes in morton order
      for mortonidx in range(0, lastzindex, 64): 

        print "Working on batch {} at {}".format( mortonidx, ocplib.MortonXYZ(mortonidx) )
        
        # call the range query
        self.db.queryRange ( mortonidx, mortonidx+64, l );

        # Flag to indicate no data.  No update query
        somedata = False

        # get the first cube
        [key,cube]  = self.db.getNextCube ()

        #  if there's a cube, there's data
        if key != None:
          somedata = True

        while key != None:

          xyz = ocplib.MortonXYZ ( key )

          # Compute the offset in the output data cube 
          #  we are placing 4x4x4 input blocks into a 2x2x4 cube 
          offset = [(xyz[0]%4)*(xcubedim/2), (xyz[1]%4)*(ycubedim/2), (xyz[2]%4)*zcubedim]

          print "res : zindex = ", l, ":", key, ", location", ocplib.MortonXYZ(key)

          # add the contribution of the cube in the hierarchy
          #self.addData ( cube, outdata, offset )
          # use the cython version
          addData_cy ( cube, outdata, offset )

          # Get the next value
          [key,cube]  = self.db.getNextCube ()

        # Now store the data 
        if somedata == True:

          #  Get the base location of this batch
          xyzout = ocplib.MortonXYZ ( mortonidx )

          outcorner = [ xyzout[0]/2*xcubedim, xyzout[1]/2*ycubedim, xyzout[2]*zcubedim ]

          #  Data stored in z,y,x order dims in x,y,z
          outdim = [ outdata.shape[2], outdata.shape[1], outdata.shape[0]]

          # Preserve annotations made at the specified level RBTODO fix me
          self.db.annotateDense ( outcorner, l+1, outdata, 'O' )
          self.db.conn.commit()
            
          # zero the output buffer
          outdata = np.zeros ([zcubedim*4, ycubedim*2, xcubedim*2])

        else:
          print "No data in this batch"
    
