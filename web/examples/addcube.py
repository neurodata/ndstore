import argparse
import empaths
import dbconfig
import dbconfighayworth5nm
import numpy as np
import urllib, urllib2
import cStringIO
import sys

import tempfile
import h5py

import anncube
import anndb
import zindex

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
  parser.add_argument('--dataoption', action="store", help='Choice of how to handle data overwrite, preserve or exception', default=None)
  parser.add_argument('--annoid', action="store", type=int, help='Specify an identifier.  Server chooses otherwise.', default=0)

  result = parser.parse_args()
  voxlist= []

  for k in range (result.zlow,result.zhigh):
    for j in range (result.ylow,result.yhigh):
      for i in range (result.xlow,result.xhigh):
        voxlist.append ( [ i,j,k ] )

  # Build a minimal hdf5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

# RBTODO test with setting identifier
  h5fh.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=result.annoid )
  h5fh.create_dataset ( "RESOLUTION", (1,), np.uint32, data=result.resolution )
  h5fh.create_dataset ( "VOXELS", (len(voxlist),3), np.uint32, data=voxlist )

  
  if result.dataoption:  
    if result.dataoption not in ('overwrite','preserve','exception'):
      print "Illegal data option %s" % result.dataoption
      sys.exit(-1)
    else:
      url = 'http://%s/annotate/%s/%s/' % ( result.baseurl, result.token, result.dataoption )
  else:
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




