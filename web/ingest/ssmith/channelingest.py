import numpy as np
import argparse
import cStringIO
import urllib2
import sys
import zlib
import zindex
import MySQLdb
from libtiff import TIFF


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

  # use the projDBs conncetion
  cursor = projdb.conn.cursor ()

  tif = TIFF.open(result.filename, mode='r')
  _ximgsz = tif.GetField("ImageWidth")
  _yimgsz = tif.GetField("ImageLength")
  _imagejinfo = tif.GetField("ImageDescription")

  imarray = np.zeros ( [result.numslices, _yimgsz, _ximgsz], dtype=np.uint16 )

  sliceno=0
  for im in tif.iter_images():
    imarray[sliceno,:,:] = im

    tifo = TIFF.open("/tmp/t.tif", mode="w")
    tifo.write_image( im )
    tif.close()
    sys.exit(0)
    
    sliceno+=1

  assert sliceno==result.numslices

#  import cutouttotiff
#  cutouttotiff.cubeToTIFFs ( imarray[:,:,:], '/data/tmp/slice' )
#  sys.exit(0)
  
  xlimit = (_ximgsz-1) / xcubedim + 1
  ylimit = (_yimgsz-1) / ycubedim + 1

  for z in range(0,2):
    conn.commit()
    for y in range(0,4):
      for x in range(0,4):

        zmin = z*16
        zmax = min((z+1)*16,30)
        zmaxrel = ((zmax-1) % 16) + 1 
        ymin = y*128
        ymax = (y+1)*128
        xmin = x*128
        xmax = (x+1)*128

        key = zindex.XYZMorton ( [x,y,z] )

        dataout = np.zeros([16,128,128],dtype=np.uint8)

        dataout[0:zmaxrel,0:128,0:128] = imarray[zmin:zmax,ymin:ymax,xmin:xmax]

        url = 'http://localhost:8000/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.token, 0, xmin, xmax, ymin, ymax, zmin, zmax )

        print url, dataout.shape, np.unique(dataout)

        # Encode the voxelist an pickle
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, dataout )

        cdz = zlib.compress (fileobj.getvalue())

        # Build the post request
        req = urllib2.Request(url, cdz)
        response = urllib2.urlopen(req)
        the_page = response.read()

if __name__ == "__main__":
  main()
