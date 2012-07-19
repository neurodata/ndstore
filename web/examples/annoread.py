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
  parser.add_argument('--voxels', action='store_true', help='Return data as a list of voxels.')
  parser.add_argument('--resolution', action="store", help='Resolution at which you want the voxels.  Defaults to the annotation database resolution.', default=None)
  parser.add_argument('--cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.', default=None)
  parser.add_argument('--output', action="store", help='File name to output the HDF5 file.', default=None)

  result = parser.parse_args()

  if result.voxels and result.resolution != None:
    url = "http://%s/annotate/%s/%s/voxels/%s/" % (result.baseurl,result.token,result.annid, result.resolution)
  elif result.voxels:
  # RBTODO does this work?
    url = "http://%s/annotate/%s/%s/voxels/" % (result.baseurl,result.token,result.annid)
  elif result.cutout != None:
    url = "http://%s/annotate/%s/%s/cutout/%s/" % (result.baseurl,result.token,result.annid, result.cutout)
  else:
    url = "http://%s/annotate/%s/%s/" % (result.baseurl,result.token,result.annid)

  print url

  # Get annotation in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s. %s" % (e.code,e.read()) 
    sys.exit(0)

  # create an in memory h5 file
  if result.output == None:
    # Read into a temporary file
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( f.read() )
    tmpfile.tell()
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  # unless an output file was requested
  else:
    fh = open ( result.output, 'w' )
    fh.write ( f.read() )
    fh.tell()
    h5f = h5py.File ( result.output )

  anno = h5ann.H5toAnnotation ( h5f )

  pprint(vars(anno))
  if h5f.get('VOXELS'):
    print "Voxel list for object:"
    print h5f['VOXELS'][:]
  elif result.voxels:
    print "No voxels found at this resolution"

  if h5f.get('CUTOUT') and h5f.get('XYZOFFSET'):
    print "Cutout at corner %s dim %s = " % (h5f['XYZOFFSET'][:],h5f['CUTOUT'].shape)
    print h5f['CUTOUT'][:,:,:]


  h5f.flush()
  h5f.close()
 

if __name__ == "__main__":
  main()

