import urllib2
import zlib
import StringIO
import numpy as np
import argparse
import cStringIO
import sys

def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('dataset', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int)
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  url = 'http://' + result.baseurl + '/emca/' + result.dataset + '/npz/' +\
            str(result.resolution) + "/" +\
            str(result.xlow) + "," + str(result.xhigh) + "/" +\
            str(result.ylow) + "," + str(result.yhigh) + "/" +\
            str(result.zlow) + "," + str(result.zhigh) + "/"\

  print "Getting URL",  url

  #  Grab the bottom corner of the cutout
  xoffset = result.xlow
  yoffset = result.ylow
  zoffset = result.zlow

  # Get cube in question
  f = urllib2.urlopen ( url )

  zdata = f.read ()

  # get the data out of the compressed blob
  pagestr = zlib.decompress ( zdata[:] )
  pagefobj = StringIO.StringIO ( pagestr )
  cube = np.load ( pagefobj )

  voxlist= []

  # Again, should the interface be all zyx
  it = np.nditer ( cube, flags=['multi_index'])
  while not it.finished:
    if it[0] < 25:
      voxlist.append ( [ it.multi_index[2]+xoffset,\
                         it.multi_index[1]+yoffset,\
                         it.multi_index[0]+zoffset ] )
    it.iternext()

  url = 'http://%s/emca/%s/npvoxels/%s/%s/' % (result.baseurl, result.token, result.annid, result.resolution)

  print url

  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, voxlist )

  # Build the post request
  try:
    req = urllib2.Request(url, fileobj.getvalue())
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)

  the_page = response.read()

  print the_page


if __name__ == "__main__":
      main()



