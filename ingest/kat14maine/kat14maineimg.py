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

import pdb
#
# ingest the tiff files into the database
#

""" This file is customized for Bobby's low resolution image data called Maine. \
    We read the images as tif files and ingest them into the database.
"""

def main():

  parser = argparse.ArgumentParser(description='Ingest the TIFF data')
  parser.add_argument('token', action="store", help='Token for the project')
  parser.add_argument('path', action="store", help='Directory with the image files')
  
  result = parser.parse_args()
  
  resolution = 0

  #Load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim) = proj.datasetcfg.cubedim[resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange
  batchsz = zcubedim

  batchsz = 16
  (ximagesz,yimagesz)=proj.datasetcfg.imagesz[resolution]

  # Set the image size to that of the actual image
  ximagesz = 6144
  yimagesz = 6144
  tilesz = 6144

  filelist = glob.glob( "{}*.tif".format(result.path) )

  # Get a list of the files in the directories
  for sl in range (startslice, endslice+1, batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint8 )

    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        #filenm = result.path + '{:0>4}_r1-c1_w01_s01_sec01_'.format(sl+b) + '{*}.tif'
        print "Opening filenm" + filelist[sl+b-1]

        img = Image.open (filelist[sl+b-1], 'r')
        imgdata = np.asarray ( img )
        slab[b,:,:] = imgdata

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b

    for y in range ( 0, yimagesz+1, ycubedim ):
      for x in range ( 0, ximagesz+1, xcubedim ):

        mortonidx = zindex.XYZMorton ( [x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
        cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint8 )

        xmin = x
        ymin = y
        xmax = ((min(ximagesz-1,x+xcubedim-1))%tilesz)+1
        ymax = ((min(yimagesz-1,y+ycubedim-1))%tilesz)+1
        
        #xmax = min ( ximagesz, x+xcubedim )
        #ymax = min ( yimagesz, y+ycubedim )
        zmin = 0
        zmax = min(sl+zcubedim, endslice+1)

        cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
        
        # Create the DB Blob
        fileobj = cStringIO.StringIO()
        np.save ( fileobj, cubedata )
        cdz = zlib.compress ( fileobj.getvalue() )

        # insert the blob into the database
        cursor = db.conn.cursor()
        sql = "INSERT INTO res{} (zindex, cube) VALUES (%s, %s)".format(int(resolution))
        cursor.execute(sql, (mortonidx, cdz))
        cursor.close()

      print " Commiting at x={}, y={}, z={}".format(x, y, sl)
    db.conn.commit()

    slab = None


if __name__ == "__main__":
  main()
