import argparse

import numpy as np
from PIL import Image

import ocppaths
import ocpcarest

import zindex

import anydbm
import multiprocessing
import pdb
#
#  ingest the PNG files into the database
#

"""This file is super-customized for Mitya's FlyEM data."""

# Stuff we make take from a config or the command line in the future
#ximagesz = 12000
#yimagesz = 12000

parser = argparse.ArgumentParser(description='Ingest the FlyEM image data.')
parser.add_argument('baseurl', action="store", help='Base URL to of ocp service no http://, e.  g. openconnecto.me')
parser.add_argument('token', action="store", help='Token for the annotation project.')
parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
parser.add_argument('process', action="store", help='Number of processes.')

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

batchsz=16
totalslices = range(startslice,endslice,16)
totalprocs = int(result.process)
#global anydb
#pdb.set_trace()
#anydb = anydbm.open('bodydict','r')
#anydb = dict(anydb)

def parallelwrite(slicenumber):
  
  # Accessing the dict in dbm
  #anydb = anydbm.open('bodydict','r')

  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  #print slicenumber
  startslice = slicenumber
  endslice = startslice+16

  # Get a list of the files in the directories
  for sl in range (startslice, endslice+1, batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint32 )
   
    for b in range ( batchsz ):

      if ( sl + b <= endslice and sl + b<=1460 ):

        # raw data
        filenm = result.path + '/superpixel.' + '{:0>5}'.format(sl+b) + '.png'
        #print "Opening filenm " + filenm
        
        img = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( img )
        #Adding new lines
        anydb = anydbm.open('bodydict2','r')
        superpixelarray = imgdata[:,:,0] + (np.uint32(imgdata[:,:,1])<<8)
        newdata = np.zeros([superpixelarray.shape[0],superpixelarray.shape[1]], dtype=np.uint32)
        #print "slice",sl+b,"batch",sl
        print sl+b,multiprocessing.current_process()
        for i in range(superpixelarray.shape[0]):
          for j in range(superpixelarray.shape[1]):
            key = str(sl)+','+str(superpixelarray[i,j])
            if( key not in anydb):
              f = open('missing_keys', 'a')
              f.write(key+'\n')
              f.close()
              print "Error Detected Writing to File"
              dictvalue = '0'
            else:
              dictvalue = anydb.get( key )
            newdata[i,j] = int(dictvalue)
        slab[b,:,:] = newdata
        print "end of slice:",sl+b
        anydb.close()
        
    print "Entering commit phase"

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
        db.annotateDense ((x,y,sl-startslice), resolution, cubedata, 'O')

      print "Commiting at x=%s, y=%s, z=%s" % (x,y,sl)
      db.conn.commit()
  return None

def run():
  flypool = multiprocessing.Pool(totalprocs)
  flypool.map(parallelwrite, totalslices, 16)

if __name__ == "__main__":
  run()
