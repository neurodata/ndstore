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
from PIL import Image
import zlib

import ocpcaproj
import ocpcadb
import ocplib
from ocpcaerror import OCPCAError

from ocpca_cy import addDataToZSliceStack_cy
from ocpca_cy import addDataToIsotropicStack_cy


#RBRM testing code
#
def getAnnValue ( value00, value01, value10, value11 ):
  """Determine the annotation value at the next level of the hierarchy from a 2x2.
      take the first non-zero element or take the first repeated element.
   """

  # The following block of code places the majority annotation into value
  # start with 00
  value = value00

  # put 01 in if not 00
  # if they are the same, that's fine
  if value == 0:
    value = value01

  if value10 != 0:
    if value == 0:
      value = value10
    # if this value matches a previous it is 2 out of 4
    elif value10 == value00 or value10 == value01:
      value = value10

  if value11 != 0:
    if value == 0:
      value = value11
    elif value11==value00 or value11==value01 or value11==value10:
      value = value11

  return value


def addDataToIsotropicStack ( cube, output, offset ):
    """Add the contribution of the input data to the next level at the given offset in the output cube"""

    for z in range (cube.data.shape[0]/2):
      for y in range (cube.data.shape[1]/2):
        for x in range (cube.data.shape[2]/2):

            # not perfect take a value from either slice.  Not a majority over all.
            value = getAnnValue (cube.data[z*2,y*2,x*2],cube.data[z*2,y*2,x*2+1],cube.data[z*2,y*2+1,x*2],cube.data[z*2,y*2+1,x*2+1])
            if value == 0:
              value = getAnnValue (cube.data[z*2+1,y*2,x*2],cube.data[z*2+1,y*2,x*2+1],cube.data[z*2+1,y*2+1,x*2],cube.data[z*2+1,y*2+1,x*2+1])

            try:
              output [ z+offset[2], y+offset[1], x+offset[0] ] = value
            except:
              import pdb; pdb.set_trace()


"""Construct a hierarchy off of a completed database."""

def buildStack ( token, resolution=None ):
  """Wrapper for the different datatypes """

  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )
  
    if proj.getProjectType() in ocpcaproj.ANNOTATION_PROJECTS:

      try:
        clearStack(token)
        buildAnnoStack( proj, resolution )
        proj.setPropagate ( ocpcaproj.PROPAGATED )
        projdb.updatePropagate ( proj )

      except MySQLdb.Error, e:
        proj.setPropagate ( ocpcaproj.NOT_PROPAGATED )
        projdb.updatePropagate ( proj )
        logger.error ( "Error in propagating the database {}".format(token) )
        raise OCPCAError ( "Error in the propagating the project {}".format(token) )

    elif proj.getProjectType() in ocpcaproj.IMAGE_PROJECTS:

      try:
        buildImageStack( proj, resolution )
      except MySQLdb.Error, e:
        logger.error ( "Error in building image stack {}".format(token) )
        raise OCPCAError ( "Error in the building image stack {}".format(token) )


def clearStack ( token ):
  """ Clear a OCP stack for a given project """


  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )
  
  with closing ( ocpcadb.OCPCADB (proj) ) as db:
    
    # Clear the database
    for l in range(proj.getResolution(), proj.datasetcfg.resolutions[-1]):
      
        sql = "TRUNCATE table res{};".format(l+1)
        sql += "TRUNCATE table raw{};".format(l+1)
        sql += "TRUNCATE table idx{};".format(l+1)
        if proj.getExceptions == ocpcaproj.EXCEPTION_TRUE:
          sql += "TRUNCATE table exec{};".format(l+1)

        try:
          print sql
          db.conn.cursor().execute(sql)
          db.conn.commit()
        except MySQLdb.Error, e:
          logger.error ("Error truncating the table. {}".format(e))
          raise
        finally:
          db.conn.cursor().close()


#    elif proj.getProjectType ()in ocpcaproj.COMPOSITE_PROJECTS:
#      buildAnnoStack( proj, resolution )
#      pass
#    else:
#      logger.warning ( "Build function not supported for this datatype {}".format(ocpcaproj.getProjectType()) )
#      raise OCPCAError ( "Build function not supported for this datatype {}".format(ocpcaproj.getProjectType()) )


def buildAnnoStack ( proj, resolution=None ):
  """ Build the hierarchy for annotations """
  
  with closing ( ocpcadb.OCPCADB (proj) ) as db:

    # pick a resolution
    if resolution == None:
      startresolution=proj.getResolution()
    else:
      startresolution = resolution

    scaling = proj.datasetcfg.scalingoption
  
    for  l in range ( startresolution, len(proj.datasetcfg.resolutions)-1 ):

      # Get the source database sizes
      [ximagesz, yimagesz, zimagesz] = proj.datasetcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = proj.datasetcfg.cubedim [ l ]

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      zlimit = zimagesz / zcubedim

      #  Choose constants that work for all resolutions. recall that cube size changes from 128x128x16 to 64*64*64
      # RBTODO derive dtype from project
      if scaling == ocpcaproj.ZSLICES:
        outdata = np.zeros ( [ zcubedim*4, ycubedim*2, xcubedim*2 ], dtype=proj.getDataType() )
      elif scaling == ocpcaproj.ISOTROPIC:
        outdata = np.zeros ( [ zcubedim*2,  ycubedim*2, xcubedim*2 ], dtype=proj.getDataType() )
      else:
        logger.error ( "Invalid scaling option in project = {}".format(scaling) )
        raise OCPCAError ( "Invalid scaling option in project = {}".format(scaling)) 

      # Round up to the top of the range
      lastzindex = (ocplib.XYZMorton([xlimit,ylimit,zlimit])/64+1)*64

      # Iterate over the cubes in morton order
      for mortonidx in range(0, lastzindex, 64): 

        print "Working on batch {} at {}. Resolution {}".format( mortonidx, ocplib.MortonXYZ(mortonidx), l )
        
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

          print "res : zindex = ", l, ":", key, ", location", ocplib.MortonXYZ(key)

          if scaling == ocpcaproj.ZSLICES:

            # Compute the offset in the output data cube 
            #  we are placing 4x4x4 input blocks into a 2x2x4 cube 
            offset = [(xyz[0]%4)*(xcubedim/2), (xyz[1]%4)*(ycubedim/2), (xyz[2]%4)*zcubedim]

            # add the contribution of the cube in the hierarchy
            #self.addData ( cube, outdata, offset )
            # use the cython version
            addDataToZSliceStack_cy ( cube, outdata, offset )

          elif scaling == ocpcaproj.ISOTROPIC:

            # Compute the offset in the output data cube 
            #  we are placing 4x4x4 input blocks into a 2x2x2 cube 
            offset = [(xyz[0]%4)*(xcubedim/2), (xyz[1]%4)*(ycubedim/2), (xyz[2]%4)*(zcubedim/2)]

            # use python version for debugging
            addDataToIsotropicStack ( cube, outdata, offset )

          # Get the next value
          [key,cube]  = db.getNextCube ()

        # Now store the data 
        if somedata == True:

          #  Get the base location of this batch
          xyzout = ocplib.MortonXYZ ( mortonidx )

          # adjust to output corner for scale.
          if scaling == ocpcaproj.ZSLICES:
            outcorner = [ xyzout[0]*xcubedim/2, xyzout[1]*ycubedim/2, xyzout[2]*zcubedim ]
          elif scaling == ocpcaproj.ISOTROPIC:
            outcorner = [ xyzout[0]*xcubedim/2, xyzout[1]*ycubedim/2, xyzout[2]*zcubedim/2 ]

          #  Data stored in z,y,x order dims in x,y,z
          outdim = [ outdata.shape[2], outdata.shape[1], outdata.shape[0]]

          # Preserve annotations made at the specified level
          # KL check that the P option preserves annotations?  RB changed from O
          db.annotateDense ( outcorner, l+1, outdata, 'P' )
          db.conn.commit()
          print "Committed"
            
          # zero the output buffer
          outdata = np.zeros ([zcubedim*4, ycubedim*2, xcubedim*2])

        else:
          print "No data in this batch"
    

def buildImageStack ( proj, resolution ):
  """Build the hierarchy of images"""

  with closing ( ocpcadb.OCPCADB (proj) ) as db:

    # pick a resolution
    if resolution == None:
      startresolution=proj.getResolution()
    else:
      startresolution = resolution

    scaling = proj.datasetcfg.scalingoption

    for l in range ( startresolution, len(proj.datasetcfg.resolutions)-1 ):

      # Get the source database sizes
      [ximagesz, yimagesz, zimagesz] = proj.datasetcfg.imagesz [ l+1 ]
      [xcubedim, ycubedim, zcubedim] = proj.datasetcfg.cubedim [ l+1 ]

      if scaling == ocpcaproj.ZSLICES:
        xscale = 2
        yscale = 2
        zscale = 1
      elif scaling == ocpcaproj.ISOTROPIC:
        xscale = 2
        yscale = 2
        zscale = 2
      else:
        logger.error ( "Invalid scaling option in project = {}".format(scaling) )
        raise OCPCAError ( "Invalid scaling option in project = {}".format(scaling)) 

      biggercubedim = [xcubedim*xscale,ycubedim*yscale,zcubedim*zscale]

      # Set the limits for iteration on the number of cubes in each dimension
      # RBTODO These limits may be wrong for even (see channelingest.py)
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      zlimit = zimagesz / zcubedim

      cursor = db.conn.cursor()

      for z in range(zlimit):
        for y in range(ylimit):
          db.conn.commit()
          for x in range(xlimit):

            # cutout the data at the resolution
            olddata = db.cutout ( [ x*xscale*xcubedim, y*yscale*ycubedim, z*zscale*zcubedim ], biggercubedim, l ).data

            #olddata target array for the new data (z,y,x) order
            newdata = np.zeros([zcubedim,ycubedim,xcubedim], dtype=proj.getDatatype())

            for sl in range(zcubedim):

              if scaling == ocpcaproj.ZSLICES:

                # Convert each slice to an image
                # 8-bit option
                if olddata.dtype==np.uint8:
                  slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'L', 0, 1 )
                elif olddata.dtype==np.uint16:
                  slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'I;16', 0, 1 )
                elif olddata.dtype==np.float32:
                  slimage = Image.frombuffer ( 'F', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'F', 0, 1 )

              elif scaling == ocpcaproj.ISOTROPIC:

                # KLTODO it's probably worth doing a ctypes implementation of the following vectorized function it's slow
                if olddata.dtype==np.uint8:
                  vec_func = np.vectorize ( lambda a,b: a if b==0 else (b if a ==0 else np.uint8((a+b)/2))) 
                  mergedata = vec_func ( olddata[sl*2,:,:], olddata[sl*2+1,:,:] )
                  slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), mergedata.flatten(), 'raw', 'L', 0, 1 )
                elif olddata.dtype==np.uint16:
                  vec_func = np.vectorize ( lambda a,b: a if b==0 else (b if a ==0 else np.uint16((a+b)/2))) 
                  mergedata = vec_func ( olddata[sl*2,:,:], olddata[sl*2+1,:,:] )
                  slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), mergedata.flatten(), 'raw', 'I;16', 0, 1 )
                elif olddata.dtype==np.float32:
                  vec_func = np.vectorize ( lambda a,b: a if b==0 else (b if a ==0 else np.float32((a+b)/2))) 
                  mergedata = vec_func ( olddata[sl*2,:,:], olddata[sl*2+1,:,:] )
                  slimage = Image.frombuffer ( 'F', (xcubedim*2,ycubedim*2), mergedata.flatten(), 'raw', 'F', 0, 1 )

              # Resize the image
              newimage = slimage.resize ( [xcubedim,ycubedim] )

              # Put to a new cube
              newdata[sl,:,:] = np.asarray ( newimage )

  
            # Compress the data
            outfobj = cStringIO.StringIO ()
            np.save ( outfobj, newdata )
            zdataout = zlib.compress (outfobj.getvalue())
            outfobj.close()

            key = ocplib.XYZMorton ( [x,y,z] )
            
            # put in the database
            sql = "INSERT INTO res" + str(l+1) + "(zindex, cube) VALUES (%s, %s)"
            print sql % (key,"x,y,z=%s,%s,%s"%(x,y,z))
            try:
              cursor.execute ( sql, (key,zdataout))
            except MySQLdb.Error, e:
              print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

      db.conn.commit()
