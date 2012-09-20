import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Fetch an annotation as an HDF5 file')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')

  result = parser.parse_args()

  # Get annotation in question
  try:
    import httplib
    conn = httplib.HTTPConnection ( "%s" % ( result.baseurl ))
    conn.request ( 'DELETE', '/emca/%s/%s/' % ( result.token, result.annid ))
    resp = conn.getresponse()
    content=resp.read()
  except httplib.HTTPException, e:
    print "Error %s" % (e) 
    sys.exit(0)

  print "Delete returns %s" % content

if __name__ == "__main__":
  main()

