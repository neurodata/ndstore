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
import scipy.ndimage.interpolation
import cStringIO
from PIL import Image
import zlib
import MySQLdb

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import zindex

"""Construct an image hierarchy up from a given resolution"""

class ImgStack:
  """Stack of images."""

  def __init__(self, token):
    """Load the database and project"""

    projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.imgDB = ocpcadb.OCPCADB ( self.proj )

    self.scaling = self.proj.datasetcfg.scalingoption


  def buildStack ( self, startlevel ):
    """Build the hierarchy of images"""

    for  l in range ( startlevel, len(self.proj.datasetcfg.resolutions) ):

      # Get the source database sizes
      [ximagesz, yimagesz, zimagesz] = self.proj.datasetcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ l ]

      if self.scaling == ocpcaproj.ZSLICES:
        xscale = 2
        yscale = 2
        zscale = 1
      elif self.scaling == ocpcaproj.ISOTROPIC:
        xscale = 2
        yscale = 2
        zscale = 2
      biggercubedim = [xcubedim*xscale,ycubedim*yscale,zcubedim*zscale]

      # Set the limits for iteration on the number of cubes in each dimension
      # RBTODO These limits may be wrong for even (see channelingest.py)
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      zlimit = zimagesz / zcubedim

      cursor = self.imgDB.conn.cursor()

      for z in range(zlimit):
        for y in range(ylimit):
          self.imgDB.conn.commit()
          for x in range(xlimit):

            # cutout the data at the -1 resolution
            olddata = self.imgDB.cutout ( [ x*xscale*xcubedim, y*yscale*ycubedim, z*zscale*zcubedim ], biggercubedim, l-1 ).data

            #olddata target array for the new data (z,y,x) order
            newdata = np.zeros([zcubedim,ycubedim,xcubedim], dtype=olddata.dtype)

            for sl in range(zcubedim):

              if self.scaling == ocpcaproj.ZSLICES:

                # Convert each slice to an image
                # 8-bit option
                if olddata.dtype==np.uint8:
                  slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'L', 0, 1 )
                elif olddata.dtype==np.uint16:
                  slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'I;16', 0, 1 )
                elif olddata.dtype==np.float32:
                  slimage = Image.frombuffer ( 'F', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'F', 0, 1 )

              elif self.scaling == ocpcaproj.ISOTROPIC:

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

            key = zindex.XYZMorton ( [x,y,z] )
            
            # put in the database
            sql = "INSERT INTO res" + str(l) + "(zindex, cube) VALUES (%s, %s)"
            print sql % (key,"x,y,z=%s,%s,%s"%(x,y,z))
            try:
              cursor.execute ( sql, (key,zdataout))
            except MySQLdb.Error, e:
              print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

      self.imgDB.conn.commit()

def main():

  parser = argparse.ArgumentParser(description='Build an image stack')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Start (highest) resolution to build')
  
  result = parser.parse_args()

  # Create the annotation stack
  imgstack = ImgStack ( result.token )

  # Iterate over the database creating the hierarchy
  imgstack.buildStack ( result.resolution )
  


if __name__ == "__main__":
  main()

