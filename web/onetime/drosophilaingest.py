import numpy as np
import argparse
import cStringIO
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
  parser.add_argument('file', action="store" )

  result = parser.parse_args()

  conn = MySQLdb.connect (host = 'localhost',
                            user = 'brain',
                            passwd = '88brain88',
                            db = result.dbname)

  cursor = conn.cursor ()

  #Load the TIFF stack
  im = Image.open(result.file)

  imarray = np.zeros ( [_endslice-_startslice+1, _ytilesize, _xtilesize], dtype=np.uint8 )
  for i in range ( _startslice, _endslice+1 ):
    im.seek(i)
    imarray[i,:,:] = np.array(im)

  for z in range(1,2):
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

        # Compress the data
        outfobj = cStringIO.StringIO ()
        np.save ( outfobj, dataout )
        zdataout = zlib.compress (outfobj.getvalue())
        outfobj.close()

        # Put in the database
        sql = "INSERT INTO res0 (zindex, cube) VALUES (%s, %s)"
        try:
          cursor.execute ( sql, (key,zdataout))
          conn.commit()
        except MySQLdb.Error, e:
          print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

if __name__ == "__main__":
  main()
