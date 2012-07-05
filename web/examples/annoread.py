import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
import tempfile
import h5py

import empaths
import h5ann
from pprint import pprint



def main():

  parser = argparse.ArgumentParser(description='Fetch an annotation as an HDF5 file')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--option', action="store", help='How you want the data: nodata list cube')

  result = parser.parse_args()

  # Get annotation in question
  try:
    url = "http://%s/annotate/%s/%s/" % (result.baseurl,result.token,result.annid)
    f = urllib2.urlopen ( url )
  except urllib2.URLError:
    print "Failed to get URL", url
    sys.exit(0)

  print url

  # This feels like one more copy than is needed
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  anno = h5ann.H5toAnnotation ( h5f )

  pprint(vars(anno))


if __name__ == "__main__":

      main()

