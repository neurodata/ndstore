import argparse
import cStringIO
import urllib2
import sys
import zlib
import zindex
import MySQLdb
from PIL import Image
import empaths
import emcaproj
import emcadb
import dbconfig
import imagecube
import numpy as np


#assume a 0 resolution level for now for ingest
RESOLUTION = 0

def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', type=int, action="store" )
  parser.add_argument('path', action="store" )
  parser.add_argument('numslices', type=int, action="store" )

  result = parser.parse_args()

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( result.token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )

  _ximgsz = None
  _yimgsz = None

  for sl in range(result.numslices):

    filenm = result.path + '/' + '{:0>4}'.format(sl) + '.png'
    print filenm
    img = Image.open ( filenm, "r" )

    if _ximgsz==None and _yimgsz==None:
      _ximgsz,_yimgsz = img.size
      imarray = np.zeros ( [result.numslices, _yimgsz, _ximgsz], dtype=np.uint16 )
    else:
      assert _ximgsz == img.size[0] and _yimgsz == img.size[1]

    imarray[sl,:,:] = np.asarray ( img )

  # get the size of the cube
  xcubedim,ycubedim,zcubedim = dbcfg.cubedim[0]
  
  # and the limits of iteration
  xlimit = (_ximgsz-1) / xcubedim + 1
  ylimit = (_yimgsz-1) / ycubedim + 1
  zlimit = (result.numslices-1) / zcubedim + 1

  # open the database
  db = emcadb.EMCADB ( dbcfg, proj )

  # get a db cursor 
  cursor = db.conn.cursor()

  for z in range(zlimit):
    db.commit()
    for y in range(ylimit):
      for x in range(xlimit):

        zmin = z*zcubedim
        zmax = min((z+1)*zcubedim,result.numslices)
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
        cube = imagecube.ImageCube16 ( [xcubedim,ycubedim,zcubedim] )

        # data for this key
        cube.data[0:zmaxrel,0:ymaxrel,0:xmaxrel] = imarray[zmin:zmax,ymin:ymax,xmin:xmax]

        # compress the cube
        npz = cube.toNPZ ()

        # add the cube to the database
        sql = "INSERT INTO " + proj.getTable(RESOLUTION) +  "(channel, zindex, cube) VALUES (%s, %s, %s)"
        print sql
        try:
          cursor.execute ( sql, (result.channel, key, npz))
        except MySQLdb.Error, e:
          raise ANNError ( "Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

  db.conn.commit()


if __name__ == "__main__":
  main()

