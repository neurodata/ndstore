import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py


# Annotation types
anno_names = { 1:'ANNO_ANNOTATION',\
               2:'ANNO_SYNAPSE',\
               3:'ANNO_SEED',\
               4:'ANNO_SEGMENT',\
               5:'ANNO_NEURON',\
               6:'ANNO_ORGANELLE' }

def main():

  parser = argparse.ArgumentParser(description='Fetch an annotation as an HDF5 file')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--voxels', action='store_true', help='Return data as a list of voxels.')
  parser.add_argument('--resolution', action="store", help='Resolution at which you want the voxels.  Defaults to the annotation database resolution.', default=None)
  parser.add_argument('--cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.', default=None)
  parser.add_argument('--output', action="store", help='File name to output the HDF5 file.', default=None)
  parser.add_argument('--tightcutout', action='store_true', help='Return a cutout as a bounding box. Requires a resolution')
  parser.add_argument('--boundingbox', action='store_true', help='Return a the bounding box with no data. Requires a resolution')

  result = parser.parse_args()

  if result.voxels:
    if result.resolution == None:
      url = "http://%s/emca/%s/%s/voxels/" % (result.baseurl,result.token,result.annid)
    else:
      url = "http://%s/emca/%s/%s/voxels/%s/" % (result.baseurl,result.token,result.annid, result.resolution)
  elif result.cutout != None:
    url = "http://%s/emca/%s/%s/cutout/%s/" % (result.baseurl,result.token,result.annid, result.cutout)
  elif result.tightcutout: 
    if result.resolution == None:
      url = "http://%s/emca/%s/%s/cutout/" % (result.baseurl,result.token,result.annid)
    else:
      url = "http://%s/emca/%s/%s/cutout/%s/" % (result.baseurl,result.token,result.annid, result.resolution)
  elif result.boundingbox: 
    if result.resolution == None:
      url = "http://%s/emca/%s/%s/boundingbox/" % (result.baseurl,result.token,result.annid)
    else:
      url = "http://%s/emca/%s/%s/boundingbox/%s/" % (result.baseurl,result.token,result.annid, result.resolution)
  else:
    url = "http://%s/emca/%s/%s/" % (result.baseurl,result.token,result.annid)

  print url

  # Get annotation in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    import pdb; pdb.set_trace()
    print "Failed URL", url
    print "Error %s" % (e.read()) 
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

  # assume a single annotation for now
  keys = h5f.keys()
  idgrp = h5f.get(keys[0])

  print "Annotation id: ", keys[0]
  print "Annotation type: ", anno_names[idgrp['ANNOTATION_TYPE'][0]]

  mdgrp = idgrp['METADATA']

  for field in mdgrp.keys():
    print field, mdgrp[field][:]

  if idgrp.get('VOXELS'):
    print "Voxel list for object:"
    print idgrp['VOXELS'][:]
  elif result.voxels:
    print "No voxels found at this resolution"

  if idgrp.get('CUTOUT') and idgrp.get('XYZOFFSET'):
    print "Cutout at corner %s dim %s = " % (idgrp['XYZOFFSET'][:],idgrp['CUTOUT'].shape)
    print "%s voxels match identifier in cutout" % ( len(np.nonzero(np.array(idgrp['CUTOUT'][:,:,:]))[0]))

  if idgrp.get('XYZDIMENSION') and idgrp.get('XYZOFFSET'):
    print "Bounding box corner %s dim %s = " % (idgrp['XYZOFFSET'][:],idgrp['XYZDIMENSION'][:])

  h5f.flush()
  h5f.close()

if __name__ == "__main__":
  main()

