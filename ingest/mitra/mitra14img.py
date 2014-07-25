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

import pdb
#
# ingest the tiff files into the database
#

""" This file is customized for Mitra's brain image data. \
    We first converted the data from jp2 to tiff using Kakadu \
    and then ingested it. For conversion look at jp2kakadu.py
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

  batchsz = 5
  (ximagesz,yimagesz)=proj.datasetcfg.imagesz[result.resolution]

  yimagesz = 18000
  ximagesz = 24000

  # Get a list of the files in the directories
  for sl in range (startslice, endslice+1, batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint32 )

    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        try:
          filenm = result.path + '{:0>4}'.format(sl+b) + '.tiff'
          print "Opening filenm" + filenm
          img = Image.open (filenm, 'r').convert("RGBA")
          imgdata = np.asarray ( img )
          slab[b,:,:] = np.left_shift(imgdata[:,:,3], 24, dtype=np.uint32) | np.left_shift(imgdata[:,:,2], 16, dtype=np.uint32) | np.left_shift(imgdata[:,:,1], 8, dtype=np.uint32) | np.uint32(imgdata[:,:,0])
        except IOError, e:
          print e
          imgdata = np.zeros((yimagesz, ximagesz), dtype=np.uint32)
          slab[b,:,:] = imgdata

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b

    for y in range ( 0, yimagesz+1, ycubedim ):
      for x in range ( 0, ximagesz+1, xcubedim ):

        # Getting a Cube id and ingesting the data one cube at a time
        mortonidx = zindex.XYZMorton ( [x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
        cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint32 )

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
