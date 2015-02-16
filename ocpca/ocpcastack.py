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
import MySQLdb

import ocpcaproj
import ocpcadb
import ocplib
from ocpcaerror import OCPCAError


from ocpca_cy import addData_cy

"""Construct a hierarchy off of a completed database."""

def buildStack ( token, resolution=None ):
  """ Wrapper for the different datatypes """

  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadProject ( token )
  
    import pdb; pdb.set_trace()

    if proj.getProjectType() in ocpcaproj.ANNOTATION_PROJECTS:

      try:
        buildAnnoStack( token, resolution )
        proj.setPropagate ( ocpcaproj.PROPAGATED )
        projdb.updatePropagate ( proj )

      except MySQLdb.Error, e:
        proj.setPropagate ( ocpcaproj.NOT_PROPAGATED )
        projdb.updatePropagate ( proj )
        logger.error ( "Error in propagating the database {}".format(token) )
        raise OCPCAError ( "Error in the propagating the project {}".format(token) )

    elif proj.getProjectType() in ocpcaproj.IMAGE_PROJECTS:
      #RB todo image project stuff
      pass
    elif proj.getProjectType ()in ocpcaproj.COMPOSITE_PROJECTS:
      pass
    else:
      logger.warning ( "Build function not supported for this datatype {}".format(ocpcaproj.getProjectType()) )
      raise OCPCAError ( "Build function not supported for this datatype {}".format(ocpcaproj.getProjectType()) )


def buildAnnoStack ( token, resolution=None ):
  """ Build the hierarchy for annotations """
  
  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadProject ( token )
  
  with closing ( ocpcadb.OCPCADB (proj) ) as db:

    import pdb; pdb.set_trace()
    # pick a resolution
    if resolution == None:
      startresolution=proj.getResolution()
    else:
      startresolution = resolution
  
    for  l in range ( startresolution, len(proj.datasetcfg.resolutions) ):

      # Get the source database sizes
      [ximagesz, yimagesz, zimagesz] = proj.datasetcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = proj.datasetcfg.cubedim [ l ]

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      zlimit = zimagesz / zcubedim

      #  Choose constants that work for all resolutions. recall that cube size changes from 128x128x16 to 64*64*64
      outdata = np.zeros ( [ zcubedim*4, ycubedim*2, xcubedim*2 ] )

      # Round up to the top of the range
      lastzindex = (ocplib.XYZMorton([xlimit,ylimit,zlimit])/64+1)*64

      # Iterate over the cubes in morton order
      for mortonidx in range(0, lastzindex, 64): 

        print "Working on batch {} at {}".format( mortonidx, ocplib.MortonXYZ(mortonidx) )
        
        # call the range query
        db.queryRange ( mortonidx, mortonidx+64, l );

        # Flag to indicate no data.  No update query
        somedata = False

        # get the first cube
        [key,cube]  = db.getNextCube ()

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
          [key,cube]  = db.getNextCube ()

        # Now store the data 
        if somedata == True:

          #  Get the base location of this batch
          xyzout = ocplib.MortonXYZ ( mortonidx )

          outcorner = [ xyzout[0]/2*xcubedim, xyzout[1]/2*ycubedim, xyzout[2]*zcubedim ]

          #  Data stored in z,y,x order dims in x,y,z
          outdim = [ outdata.shape[2], outdata.shape[1], outdata.shape[0]]

          # Preserve annotations made at the specified level RBTODO fix me
          db.annotateDense ( outcorner, l+1, outdata, 'O' )
          db.conn.commit()
            
          # zero the output buffer
          outdata = np.zeros ([zcubedim*4, ycubedim*2, xcubedim*2])

        else:
          print "No data in this batch"
    
