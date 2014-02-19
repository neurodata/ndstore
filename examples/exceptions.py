import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys
import tempfile
import h5py
import re

import zlib

def main():

  parser = argparse.ArgumentParser(description='Cutout a small region of the database and print the contents')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.' )

  result = parser.parse_args()

  url = 'http://%s/ca/%s/exceptions/%s/' % ( result.baseurl, result.token, result.cutout )

  # Get cube in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e) 
    sys.exit(-1)

  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.seek(0)
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  excar = np.array( h5f['exceptions'] )

  p = re.compile('^(\d+)/(\d+),(\d+)/(\d+),(\d+)/(\d+),(\d+).*')
  m = p.match ( result.cutout )
  [ res, xmin, xmax, ymin, ymax, zmin, zmax ] = map(int, m.groups())

  zmin = zmin - 2917
  zmax = zmax - 2917

  for i in range(excar.shape[0]):
    if excar[i,0] >= xmin and excar[i,0] < xmax and excar[i,1] >= ymin and excar[i,1] < ymax and excar[i,2] >= zmin and excar[i,2] < zmax:
      print excar[i,:]

if __name__ == "__main__":
  main()




