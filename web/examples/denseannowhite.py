import urllib2
import zlib
import StringIO
import numpy as np
import argparse
import cStringIO
import sys


def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  #RBTODO annotate resolution
  url = 'http://0.0.0.0:8080/hayworth5nm/npz/3/' +\
            str(result.xlow) + "," + str(result.xhigh) + "/" +\
            str(result.ylow) + "," + str(result.yhigh) + "/" +\
            str(result.zlow) + "," + str(result.zhigh) + "/"\

  print url

  #  Grab the bottom corner of the cutout
  xoffset = result.xlow
  yoffset = result.ylow
  zoffset = result.zlow

  # Get cube in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError:
    assert 0

  zdata = f.read ()

  # get the data out of the compressed blob
  pagestr = zlib.decompress ( zdata[:] )
  pagefobj = StringIO.StringIO ( pagestr )
  cube = np.load ( pagefobj )

  annodata = np.zeros( [ result.zhigh - result.zlow, result.yhigh - result.ylow, result.xhigh-result.xlow ] )

  print annodata.shape
  print cube.shape
   
  vec_func = np.vectorize ( lambda x: 0 if x < 160 else 125 ) 
  annodata = vec_func ( cube )

  url = 'http://0.0.0.0:8080/annotate/hanno/npdense/add/%s,%s/%s,%s/%s,%s/' % ( result.xlow, result.xhigh, result.ylow, result.yhigh, result.zlow, result.zhigh ) 

  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, annodata )
  cdz = zlib.compress (fileobj.getvalue())

  # Build the post request
  req = urllib2.Request(url, cdz)
  response = urllib2.urlopen(req)
  the_page = response.read()

  print the_page


if __name__ == "__main__":
      main()



