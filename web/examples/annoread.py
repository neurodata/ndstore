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
  parser.add_argument('--option', action="store", help='How you want the data: nodata voxels cutout', default='nodata')
  parser.add_argument('--resolution', action="store", help='Resolution at which you want the voxels', default=None)

  result = parser.parse_args()

  if result.resolution != None and result.option != 'nodata':
    url = "http://%s/annotate/%s/%s/%s/%s/" % (result.baseurl,result.token,result.annid, result.option, result.resolution)
  else:
    url = "http://%s/annotate/%s/%s/%s/" % (result.baseurl,result.token,result.annid, result.option)

  print url

  # Get annotation in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError:
    print "Failed to get URL", url
    sys.exit(0)

  # This feels like one more copy than is needed
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  anno = h5ann.H5toAnnotation ( h5f )

  pprint(vars(anno))

  if h5f.get('VOXELS'):
    print "Voxel list for object:"
    print h5f['VOXELS'][:]

if __name__ == "__main__":

      main()

