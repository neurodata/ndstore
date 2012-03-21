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

  voxlist= []

  # Again, should the interface be all zyx
  it = np.nditer ( cube, flags=['multi_index'])
  while not it.finished:
    if it[0] > 160:
      voxlist.append ( [ it.multi_index[2]+xoffset,\
                         it.multi_index[1]+yoffset,\
                         it.multi_index[0]+zoffset ] )
    it.iternext()

  url = 'http://0.0.0.0:8080/annotate/hanno/npvoxels/new/'

  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, voxlist )

  # Build the post request
  req = urllib2.Request(url, fileobj.getvalue())
  response = urllib2.urlopen(req)
  the_page = response.read()

  print the_page


if __name__ == "__main__":
      main()



