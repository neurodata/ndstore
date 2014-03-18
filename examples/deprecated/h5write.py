import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys
import re
import tempfile
import h5py

import zlib

def main():

  parser = argparse.ArgumentParser(description='Write a region of the database.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.' )

  parser.add_argument('--probmap', action='store_true')
  parser.add_argument('--mask', action='store_true')

  result = parser.parse_args()

  # parse the cutout
  p = re.compile('(\w+)/(\w+),(\w+)/(\w+),(\w+)/(\w+),(\w+).*$')
  m = p.match(result.cutout)
  if m != None:
    res,xlow,xhigh,ylow,yhigh,zlow,zhigh = map(int,m.groups())

  url = 'http://%s/ca/%s/hdf5/%s/' % ( result.baseurl, result.token, result.cutout )

  # if it's a probability map
  if result.probmap:
    cuboid = np.float32(np.random.random_sample ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ] ))

  elif result.mask:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint8 )

  # otherwise annotation
  else:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint32 )

  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )
  # top group is the annotation identifier
  h5fh.create_dataset ( "CUTOUT", cuboid.shape, data=cuboid )

  # get the file read
  h5fh.flush()
  tmpfile.seek(0)

  # Get cube in question
  try:
    f = urllib2.urlopen ( url, tmpfile.read()  )
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e) 
    sys.exit(-1)

if __name__ == "__main__":
  main()




