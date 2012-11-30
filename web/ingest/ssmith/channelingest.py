import argparse
import cStringIO
import urllib2
import sys
import zlib
import zindex
import MySQLdb
from libtiff import TIFF
import empaths
import emcaproj
import dbconfig
import chandb
import chancube
import numpy as np


def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', type=int, action="store" )
  parser.add_argument('filename', action="store" )
  parser.add_argument('numslices', type=int, action="store" )

  result = parser.parse_args()

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( result.token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )

  tif = TIFF.open(result.filename, mode='r')
  _ximgsz = tif.GetField("ImageWidth")
  _yimgsz = tif.GetField("ImageLength")
  _imagejinfo = tif.GetField("ImageDescription")

  imarray = np.zeros ( [result.numslices, _yimgsz, _ximgsz], dtype=np.uint16 )

  sliceno=0
  for im in tif.iter_images():
    imarray[sliceno,:,:] = im
    sliceno+=1

  assert sliceno==result.numslices
  slices = result.numslices

#  import cutouttotiff
#  cutouttotiff.cubeToTIFFs ( imarray[:,:,:], '/data/tmp/slice' )
#  sys.exit(0)

  # get the size of the cube
  xcubedim,ycubedim,zcubedim = dbcfg.cubedim[0]
  
  # and the limits of iteration
  xlimit = (_ximgsz-1) / xcubedim + 1
  ylimit = (_yimgsz-1) / ycubedim + 1
  zlimit = (slices-1) / zcubedim + 1

  # open the database
  db = chandb.ChanDB ( dbcfg, proj )

  for z in range(zlimit):
    db.commit()
    for y in range(ylimit):
      for x in range(xlimit):

        zmin = z*zcubedim
        zmax = min((z+1)*zcubedim,slices)
        zmaxrel = ((zmax-1)%zcubedim)+1 
        ymin = y*ycubedim
        ymax = min((y+1)*ycubedim,_yimgsz)
        ymaxrel = ((ymax-1)%ycubedim)+1
        xmin = x*xcubedim
        xmax = min((x+1)*xcubedim,_ximgsz)
        xmaxrel = ((xmax-1)%xcubedim)+1

        # morton key
        key = zindex.XYZMorton ( [x,y,z] )

        # Create a channel cube
        cube = chancube.ChanCube ( [xcubedim,ycubedim,zcubedim] )

        # data for this key
        cube.data[0:zmaxrel,0:ymaxrel,0:xmaxrel] = imarray[zmin:zmax,ymin:ymax,xmin:xmax]

#        need to make a channel cube?

        db.putCube ( key, result.channel, 0, cube )

if __name__ == "__main__":
  main()
