import numpy as np
import argparse
import cStringIO
import urllib2
import sys
import zlib
import zindex
from PIL import Image
import MySQLdb


# assume a 128x128x16 cube 
_startslice = 0 
_endslice = 29 
_xtilesize = 512
_ytilesize = 512

def main():

  parser = argparse.ArgumentParser(description='Ingest a drosophilia tiff stack.')
  parser.add_argument('dbname', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('file', action="store" )

  result = parser.parse_args()

  conn = MySQLdb.connect (host = 'localhost',
                            user = 'brain',
                            passwd = '88brain88',
                            db = result.dbname)

  cursor = conn.cursor ()

  #Load the TIFF stack
  im = Image.open(result.file)

  # RBTODO this is a 16bit image.  Don't know how to read it.
  #  It won't convert into a numpy array
    
  imarray = np.zeros ( [_endslice-_startslice+1, _ytilesize, _xtilesize], dtype=np.uint32 )
  for i in range ( _startslice, _endslice+1 ):
    im.seek(i)
    print i
    imarray[i,:,:] = np.array(im.getdata()).reshape([512,512])

  print np.unique(imarray)
  print np.nonzero(imarray)

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
