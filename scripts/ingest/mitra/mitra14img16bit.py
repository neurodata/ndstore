# Copyright 2014 NeuroData (http://neurodata.io)
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
from PIL import Image
import cStringIO
import zlib

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest

import zindex
import glob
import cv2

#
# ingest the tiff files into the database
#

""" This file is customized for Mitra's brain image data. \
    It uses cv2 to read 16bit images and ingest them in the \
    OCP stack. Trying to make the script common for both 8-bit \
    and 16-bit
"""

def main():

  parser = argparse.ArgumentParser(description='Ingest the TIFF data')
  parser.add_argument('token', action="store", help='Token for the project')
  parser.add_argument('path', action="store", help='Directory with the image files')
  parser.add_argument('resolution', action="store", type=int, help='Resolution of data')

  result = parser.parse_args()
  
  #Load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim) = proj.datasetcfg.cubedim[result.resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange
  batchsz = zcubedim

  batchsz = 16
  (ximagesz,yimagesz)=proj.datasetcfg.imagesz[result.resolution]

  yimagesz = 18000
  ximagesz = 24000

  # Get a list of the files in the directories
  for sl in range (startslice, endslice+1, batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint64 )

    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        try:
          filenm = result.path + '{:0>4}'.format(sl+b) + '.tiff'
          print "Opening filenm" + filenm
          
          # Returns the image in BGR order. IN 8-bit script PIL returns it in correct order.
          imgdata = cv2.imread( filenm, -1 )
          if imgdata != None:
            slab[b,:,:] = np.left_shift(65535, 48, dtype=np.uint64) | np.left_shift(imgdata[:,:,0], 32, dtype=np.uint64) | np.left_shift(imgdata[:,:,1], 16, dtype=np.uint64) | np.uint64(imgdata[:,:,2])
          else:
            slab[b,:,:] = np.zeros( [ yimagesz, ximagesz ], dtype=np.uint64)
        except IOError, e:
          slab[b,:,:] = np.zeros( [ yimagesz, ximagesz ], dtype=np.uint64)
          print e

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b

    for y in range ( 0, yimagesz+1, ycubedim ):
      for x in range ( 0, ximagesz+1, xcubedim ):

        mortonidx = zindex.XYZMorton ( [x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
        cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint64 )

        xmin = x
        ymin = y
        xmax = min ( ximagesz, x+xcubedim )
        ymax = min ( yimagesz, y+ycubedim )
        zmin = 0
        zmax = min(sl+zcubedim, endslice+1)

        cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
        
        # Create the DB Blob
        fileobj = cStringIO.StringIO()
        np.save ( fileobj, cubedata )
        cdz = zlib.compress ( fileobj.getvalue() )

        # insert the blob into the database
        cursor = db.conn.cursor()
        sql = "INSERT INTO res{} (zindex, cube) VALUES (%s, %s)".format(int(result.resolution))
        cursor.execute(sql, (mortonidx, cdz))
        cursor.close()

      print " Commiting at x={}, y={}, z={}".format(x, y, sl)
    db.conn.commit()
  
    # Freeing memory
    slab = None

if __name__ == "__main__":
  main()
