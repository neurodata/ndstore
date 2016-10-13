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

import kanno_cy 

#
#  ingest the PNG files into the database
#

"""This file is super-customized for Bobby's meso-scale s1 data"""

# Stuff we make take from a config or the command line in the future
#ximagesz = 12000
#yimagesz = 12000

# number of 8192^2 tiles in each dimension
xtiles=6
ytiles=4
tilesz=8192



def main():

  parser = argparse.ArgumentParser(description='Ingest the FlyEM image data.')
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
  ximagesz = 49152
  yimagesz = 32768

  # add all of the tiles to the image
  for sl in range (startslice,endslice+1,batchsz):
    for ytile in range(ytiles):
      for xtile in range(xtiles):
       
        slab = np.zeros ( [ batchsz, tilesz, tilesz ], dtype=np.uint32 )

        for b in range ( batchsz ):
          if ( sl + b <= endslice ):

            # raw data
            filenm = result.path + '/S1Column_Localcellbodies_97-classified_export_s{:0>3}_Y{}_X{}.png'.format(sl+b,ytile,xtile) 
            print "Opening filenm " + filenm
          
            img = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( img )

            slab[b,:,:] = kanno_cy.pngto32 ( imgdata )

          # the last z offset that we ingest, if the batch ends before batchsz
          endz = b

        # Now we have a 8192x8192x16 z-aligned cube.  
        # Send it to the database.
        for y in range ( ytile*tilesz, (ytile+1)*tilesz, ycubedim ):
          for x in range ( xtile*tilesz, (xtile+1)*tilesz, xcubedim ):

            mortonidx = zindex.XYZMorton ( [ x/xcubedim, y/ycubedim, (sl-startslice)/zcubedim] )
            cubedata = np.zeros ( [zcubedim, ycubedim, xcubedim], dtype=np.uint32 )

            xmin = x%tilesz
            ymin = y%tilesz
            xmax = ((min(ximagesz-1,x+xcubedim-1))%tilesz)+1
            ymax = ((min(yimagesz-1,y+ycubedim-1))%tilesz)+1
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
            print mortonidx
            cursor.execute(sql, (mortonidx, cdz))
            cursor.close()

          print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl)
          db.conn.commit()


if __name__ == "__main__":
  main()

