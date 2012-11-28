import numpy as np
import argparse
import cStringIO
import urllib2
import sys
import zlib
import zindex
from PIL import Image
import MySQLdb


def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
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

  # get the tile size from the image
  _xtilesize,_ytilesize = im.size 

  print _xtilesize,_ytilesize

  import pdb; pdb.set_trace()

  # figure out how many images in the stack
  numslices=0;
  try:
    while(1):
      im.seek(numslices)
      numslices+=1
  except EOFError:
    print "Found slices: ", numslices

  imarray = np.zeros ( [numslices, _ytilesize, _xtilesize], dtype=np.uint16 )
  for sl in range(numslices):
    im.seek(sl)

    imarray[sl,:,:] = np.array(im.getdata()).reshape([_ytilesize,_xtilesize])
    print "Slice", sl

    import cutouttotiff
    cutouttotiff.cubeToTIFFs ( imarray[0:1,:,:], '/data/tmp/slice' )
    sys.exit(0)

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
