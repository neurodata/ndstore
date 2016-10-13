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
import kanno_cy 
import pdb

#
#  ingest the TIF files into the database
#

"""This file is super-customized for Rohanna Annotation datal. \
  This file has a bug as it starts ingesting data from 723 instead of 725. \
  For the correct script look at rhoana.py.
"""

xoffsetsz = 0
yoffsetsz = 0
zoffsetsz = 0

def main():

  parser = argparse.ArgumentParser(description='Ingest the Rohanna data.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation TIF files.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution')

  result = parser.parse_args()

  # convert to an argument
  resolution = result.resolution

  # load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim)=proj.datasetcfg.cubedim[resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange
  batchsz=zcubedim

  # This doesn't work because the image size does not match exactly the cube size
  #(ximagesz,yimagesz)=proj.datasetcfg.imagesz[resolution]
  ximagesz = 10748
  yimagesz = 12896
  
  # add all of the tiles to the image
  for sl in range (993,endslice+1,batchsz):
  
    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint32 )

    for b in range ( batchsz ):
        
      if ( sl + b <= endslice ):

        # raw data
        filenm = result.path + 'RCvesiclescleaned_s{:0>4}.png'.format(sl+b-1)
        print "Opening filenm " + filenm
        
        try:
          img = Image.open ( filenm, 'r' )
          imgdata = np.asarray ( img )
          imgdata = np.left_shift(imgdata[:,:,0], 16, dtype=np.uint32) | np.left_shift(imgdata[:,:,1], 16, dtype=np.uint32) | np.uint32(imgdata[:,:,2])
        except IOError, e:
          print e
          imgdata = np.zeros((yimagesz,ximagesz), dtype=np.uint32)
        
        slab[b,:,:] = ( imgdata )
      
      # the last z offset that we ingest, if the batch ends before batchsz
        endz = b
   
    # Now we have a 5120x5120x16 z-aligned cube.  
    # Send it to the database.
    for y in range ( 0, yimagesz, ycubedim ):
      for x in range ( 0, ximagesz, xcubedim ):

        mortonidx = zindex.XYZMorton ( [ (x)/xcubedim, (y)/ycubedim, (sl-startslice)/zcubedim] )
        cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint32 )
        test = zindex.MortonXYZ (mortonidx )
        xmin = x
        ymin = y
        xmax = min ( ximagesz, x+xcubedim )
        ymax = min ( yimagesz, y+ycubedim )
        zmin = 0
        zmax = min(sl+zcubedim,endslice+1)
        cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax,ymin:ymax,xmin:xmax]

        # check if there's anything to store
        if ( np.count_nonzero(cubedata) == 0 ):
          continue

        # create the DB BLOB
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, cubedata )
        cdz = zlib.compress (fileobj.getvalue())

        # insert the blob into the database
        cursor = db.conn.cursor()
        sql = "INSERT INTO res{} (zindex, cube) VALUES (%s, %s)".format(int(resolution))
        cursor.execute(sql, (mortonidx, cdz))
        cursor.close()
        print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl+b)
      db.conn.commit()


if __name__ == "__main__":
  main()

