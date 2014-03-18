import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
import tempfile
import h5py
import random 
import csv

from pprint import pprint


class H5Anno:

  def __init__(self):

    # Create an in-memory HDF5 file
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.h5fh = h5py.File ( self.tmpfile.name )

  def addAnno ( self, annotype, annoid, kv=None ):
    """Add an annotation to the file."""

    # Create the top level annotation id namespace
    idgrp = self.h5fh.create_group ( str(annoid) )

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    # now lets add a bunch of random values for the specific annotation type
    ann_status = random.randint(0,4)
    ann_confidence = random.random()
    ann_author = 'randal'

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    kvpairs={}
    if kv!= None:
      [ k, sym, v ] = kv.partition(':')
      kvpairs[k]=v

      # Turn our dictionary into a csv file
      fstring = cStringIO.StringIO()
      csvw = csv.writer(fstring, delimiter=',')
      csvw.writerows([r for r in kvpairs.iteritems()])

      # User-defined metadata
      mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())

    # Synapse:
    if annotype == 2:

      syn_weight = random.random()*1000.0
      syn_synapse_type = random.randint(1,9)
      syn_seeds = [ random.randint(1,1000) for x in range(5) ]

      syn_segments = [ [random.randint(1,1000),random.randint(1,1000)] for x in range(4) ]

      mdgrp.create_dataset ( "WEIGHT", (1,), np.float, data=syn_weight )
      mdgrp.create_dataset ( "SYNAPSE_TYPE", (1,), np.uint32, data=syn_synapse_type )
      mdgrp.create_dataset ( "SEEDS", (len(syn_seeds),), np.uint32, data=syn_seeds )
      mdgrp.create_dataset ( "SEGMENTS", (len(syn_segments),2), np.uint32, data=syn_segments)

    # Seed
    elif annotype == 3:

      seed_parent = random.randint(1,1000)
      seed_position = [ random.randint(1,10000) for x in range(3) ]
      seed_cubelocation = random.randint(1,9)
      seed_source = random.randint(1,1000)

      mdgrp.create_dataset ( "PARENT", (1,), np.uint32, data=seed_parent )
      mdgrp.create_dataset ( "CUBE_LOCATION", (1,), np.uint32, data=seed_cubelocation )
      mdgrp.create_dataset ( "SOURCE", (1,), np.uint32, data=seed_source )    
      mdgrp.create_dataset ( "POSITION", (3,), np.uint32, data=seed_position )

    # Segment
    elif annotype == 4:
       
      seg_parentseed = random.randint(1,100000)
      seg_segmentclass = random.randint(1,9)
      seg_neuron = random.randint(1,100000)
      seg_synapses = [ random.randint(1,100000) for x in range(5) ]
      seg_organelles = [ random.randint(1,100000) for x in range(5) ]

      mdgrp.create_dataset ( "SEGMENTCLASS", (1,), np.uint32, data=seg_segmentclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=seg_parentseed )
      mdgrp.create_dataset ( "NEURON", (1,), np.uint32, data=seg_neuron )
      mdgrp.create_dataset ( "SYNAPSES", (len(seg_synapses),), np.uint32, seg_synapses )
      mdgrp.create_dataset ( "ORGANELLES", (len(seg_organelles),), np.uint32, seg_organelles )

    # Neuron
    elif annotype == 5:

      neuron_segments = [ random.randint(1,1000) for x in range(10) ]
      mdgrp.create_dataset ( "SEGMENTS", (len(neuron_segments),), np.uint32, neuron_segments )

    # Organelle
    elif annotype == 6:

      org_parentseed = random.randint(1,100000)
      org_organelleclass = random.randint(1,9)
      org_seeds = [ random.randint(1,100000) for x in range(5) ]
      org_centroid = [ random.randint(1,10000) for x in range(3) ]

      mdgrp.create_dataset ( "ORGANELLECLASS", (1,), np.uint32, data=org_organelleclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=org_parentseed )
      mdgrp.create_dataset ( "SEEDS", (len(org_seeds),), np.uint32, org_seeds )
      mdgrp.create_dataset ( "CENTROID", (3,), np.uint32, data=org_centroid )

  def getFileObject(self):
    """Return a file object to be posted to a URL"""
    self.h5fh.flush()
    self.tmpfile.seek(0)
    # return and file object to be posted
    return self.tmpfile


  def addCutout (self, annid, cutout):
    """Add a cube of data to the HDF5 file"""

    [ resstr, xstr, ystr, zstr ] = cutout.split('/')
    ( xlowstr, xhighstr ) = xstr.split(',')
    ( ylowstr, yhighstr ) = ystr.split(',')
    ( zlowstr, zhighstr ) = zstr.split(',')

    resolution = int(resstr)
    xlow = int(xlowstr)
    xhigh = int(xhighstr)
    ylow = int(ylowstr)
    yhigh = int(yhighstr)
    zlow = int(zlowstr)
    zhigh = int(zhighstr)

    idgrp = self.h5fh[str(annid)]

    anndata = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ] )
    idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
    idgrp.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[xlow,ylow,zlow] )
    idgrp.create_dataset ( "CUTOUT", anndata.shape, np.uint32, data=anndata )


  def addVoxels(self, annid, cutout):
    """Add a cube of data to the HDF5 file as a list of voxels"""

    [ resstr, xstr, ystr, zstr ] = cutout.split('/')
    ( xlowstr, xhighstr ) = xstr.split(',')
    ( ylowstr, yhighstr ) = ystr.split(',')
    ( zlowstr, zhighstr ) = zstr.split(',')

    resolution = int(resstr)
    xlow = int(xlowstr)
    xhigh = int(xhighstr)
    ylow = int(ylowstr)
    yhigh = int(yhighstr)
    zlow = int(zlowstr)
    zhigh = int(zhighstr)

    voxlist =[]

    for k in range (zlow,zhigh):
      for j in range (ylow,yhigh):
        for i in range (xlow,xhigh):
          voxlist.append ( [ i,j,k ] )

    idgrp = self.h5fh[str(annid)]

    # make annid 0 if it's not an integer
    if not isinstance(annid,int):
      annid = 0

    idgrp.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=annid )
    idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
    idgrp.create_dataset ( "VOXELS", (len(voxlist),3), np.uint32, data=voxlist )


def main():

  parser = argparse.ArgumentParser(description='Write an annotation object.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('--anntype', action="store", type=int, default=1)
  parser.add_argument('--annid', action="store", type=int, help='Annotation ID to extract', default=0)
  parser.add_argument('--update', action='store_true', help='Update an existing annotation.')
  parser.add_argument('--cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.', default=None)
  parser.add_argument('--voxels', action='store_true', help='Store the voxels as a list.')
  parser.add_argument('--reduce', action='store_true', help="Remove the specified voxels from the annotation.")
  parser.add_argument('--dataonly', action='store_true', help="Data only not metadata")
  parser.add_argument('--overwrite', action='store_true', help='Overwrite exisiting annotations in the database.  Thi is the Default.')
  parser.add_argument('--preserve', action='store_true', help='Preserve exisiting annotations in the database.  Default is overwrite.')
  parser.add_argument('--exception', action='store_true', help='Store multiple nnotations at the same voxel in the database.  Default is overwrite.')
  parser.add_argument('--kv', action="store", help='key:value')
  parser.add_argument('--numobjects', action="store", type=int, default=1, help='Store multiple objects')

  result = parser.parse_args()

  h5ann = H5Anno()
  for i in range(result.numobjects):
    # either anonymous annotations ids
    if result.annid==0:
      annid = 'noid.'+str(i)
    # or a sequence starting from result.annid
    else:
      annid=result.annid+i

    # if mutliple objects and no type, insert random object types
    if result.anntype==1 and result.numobjects > 1 and not result.voxels and not result.cutout:
      anntype = random.randint(1,6)
    else:
      anntype = result.anntype

    h5ann.addAnno ( anntype, annid, result.kv )

  # debug from here
    if result.cutout:
      if result.voxels:
        h5ann.addVoxels ( annid, result.cutout )
      else:
        h5ann.addCutout ( annid, result.cutout )

  # get the file handle
  fileobj = h5ann.getFileObject()

  # Build the put URL
  if result.update:
    url = "http://%s/ca/%s/update/" % ( result.baseurl, result.token)
  elif result.dataonly:
    url = "http://%s/ca/%s/dataonly/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/ca/%s/" % ( result.baseurl, result.token)

  if result.preserve:  
    url += 'preserve/'
  elif result.exception:  
    url += 'exception/'
  elif result.overwrite:  
    url += 'overwrite/'
  elif result.reduce:  
    url += 'reduce/'

  print url

  try:
    req = urllib2.Request ( url, fileobj.read()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()

