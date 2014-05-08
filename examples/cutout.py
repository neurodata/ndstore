import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys

import zlib

def main():

  parser = argparse.ArgumentParser(description='Cutout a small region of the database and print the contents')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.' )

  result = parser.parse_args()

  url = 'http://%s/ca/%s/npz/%s/' % ( result.baseurl, result.token, result.cutout )

  # Get cube in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e) 
    sys.exit(-1)

  zdata = f.read ()

  # get the data out of the compressed blob
  pagestr = zlib.decompress ( zdata[:] )
  pagefobj = cStringIO.StringIO ( pagestr )
  cube = np.load ( pagefobj )

  print cube

  cube.tostring()

if __name__ == "__main__":
  main()




