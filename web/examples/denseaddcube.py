import argparse
import empaths
import numpy as np
import urllib, urllib2
import cStringIO
import zlib
import sys

import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Annotate a cubic a portion of the database.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  anndata = np.ones ( [ result.zhigh-result.zlow, result.yhigh-result.ylow, result.xhigh-result.xlow ] )

  # Build a minimal hdf5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

  h5fh.create_dataset ( "RESOLUTION", (1,), np.uint32, data=result.resolution )
  h5fh.create_dataset ( "XYZOFFSET", (1,3), np.uint32, data=[result.xlow,result.ylow,result.zlow] )
  h5fh.create_dataset ( "VOLUME", anndata.shape, np.uint32, data=anndata )

  url = 'http://%s/annotate/%s/' % ( result.baseurl, result.token )
  
  print url

  try:
    h5fh.flush()
    tmpfile.seek(0)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
  except urllib2.URLError:
    print "Failed to put URL", url
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()
