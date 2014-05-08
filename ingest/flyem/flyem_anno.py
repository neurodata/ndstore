import argparse
import sys
import os

import numpy as np
from PIL import Image
import cStringIO
import zlib

import ocppaths
import ocpcarest

import zindex

import anydbm
import pdb
#
#  ingest the PNG files into the database
#

"""This file is super-customized for Mitya's FlyEM data."""

# Stuff we make take from a config or the command line in the future
#ximagesz = 12000
#yimagesz = 12000



def main():

  parser = argparse.ArgumentParser(description='Ingest the FlyEM image data.')
  parser.add_argument('baseurl', action="store", help='Base URL to of ocp service no http://, e.  g. openconnecto.me')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')

  result = parser.parse_args()

  # convert to an argument
  resolution = 0

  # load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim)=proj.datasetcfg.cubedim[resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange
  batchsz=zcubedim

  # This doesn't work because the image size does not match exactly the cube size
  #(ximagesz,yimagesz)=proj.datasetcfg.imagesz[resolution]
  ximagesz = 12000
  yimagesz = 12000

  batchsz=1

  # Accessing the dict in dbm
  anydb = anydbm.open('bodydict','r')

  # Get a list of the files in the directories
  for sl in range (startslice,endslice+1,batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint32 )
   
    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        filenm = result.path + '/superpixel.' + '{:0>5}'.format(sl+b) + '.png'
        print "Opening filenm " + filenm
        
        
        img = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( img )
        #lab[b,:,:]  = kanno_cy.pngto32(imgdata)
        #Adding new lines
        superpixelarray = imgdata[:,:,0] + (np.uint32(imgdata[:,:,1])<<8)
        newdata = np.zeros([superpixelarray.shape[0],superpixelarray.shape[1]], dtype=np.uint32)
        print "slice",sl
        for i in range(superpixelarray.shape[0]):
          for j in range(superpixelarray.shape[1]):
            dictvalue = anydb.get( str(sl)+','+str(superpixelarray[i,j]) )
            newdata[i,j] = int(dictvalue)
        slab[b,:,:] = newdata
        print "end on slice:",sl
        
        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b
        continue
    continue

    # Now we have a 1024x1024x16 z-aligned cube.  
    # Send it to the database.
    for y in range ( 0, yimagesz, ycubedim ):
      for x in range ( 0, ximagesz, xcubedim ):

        mortonidx = zindex.XYZMorton ( [ x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
        cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint32 )

        xmin = x
        ymin = y
        xmax = min ( ximagesz, x+xcubedim )
        ymax = min ( yimagesz, y+ycubedim )
        zmin = 0
        zmax = min(sl+zcubedim,endslice+1)

        cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax,ymin:ymax,xmin:xmax]

        # insert the blob into the database
        db.annotateDense ((x,y,sl-startslice),resolution,cubedata,'O')

      print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl)
      db.conn.commit()


if __name__ == "__main__":
  main()

