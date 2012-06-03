import numpy as np
import urllib2
import tempfile
import h5py
import csv
import cStringIO
import collections

import sys

import empaths
import annotation
import anndb
import annproj
import dbconfig

from pprint import pprint

#
#  class to define the HDF5 format of annotations.
#

"""The HDF5 format currently looks like:

/  (Root) group:

ANNOTATION_TYPE (int)
ANNOTATION_ID (int)
OFFSET ( int[3] optional )
VOXEL_DATA ( int32 3-d array optional )

METADATA group;

 # metadata for all annotations
 CONFIDENCE (float)
 STATUS (int) 
 KVPAIRS   (string containing csv pairs)

 # for seeds

 PARENT (int)
 POSITION (int[3])
 CUBE_LOCATION (int)
 SOURCE (int)

 # for synapses:

 SYNAPSE_TYPE (int)
 WEIGHT (float)
 SEEDS (int[]) 
 SEGMENTS ( int[ ][2] )
"""


class H5Annotation:
  """Class to move data into and out of HDF5 files"""

  def __init__( self, annotype, annoid, location=None, voxels=None ):
    """Create an HDF5 file and simple structure"""

    # Create an in-memory HDF5 file
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.h5fh = h5py.File ( self.tmpfile.name )

    # Annotation type
    self.h5fh.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )
    self.h5fh.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=annoid )

    # Create a metadata group
    self.mdgrp = self.h5fh.create_group ( "METADATA" ) 

    # Zeroed data if not none
    if location != None:
      self.h5fh.create_dataset ( "OFFSET", (3,), np.uint32, data=location )     
      self.h5fh.create_dataset ( "VOXEL_DATA", voxels.shape, np.uint32, compression='gzip', data=voxels )

  def __del__ ( self ):
    """Destructor"""
    self.h5fh.close()

  def fileReader( self ):
    """Return a file read stream to be transferred as put data"""
    self.h5fh.flush()
    self.tmpfile.seek(0)
    return self.tmpfile.read()


############## Converting HDF5 to Annotations

def H5toAnnotation ( h5fh ):
  """Return an annotation constructed from the contents of this HDF5 file"""

  # get the annotation type
  annotype = h5fh['ANNOTATION_TYPE'][0]

  # And get the metadata group
  mdgrp = h5fh['METADATA']

  if annotype == annotation.ANNO_SEED:

    # Create the appropriate annotation type
    anno = annotation.AnnSeed()

    # load the seed specific metadata
    anno.parent = mdgrp['PARENT'][0]
    anno.position = mdgrp['POSITION'][:]
    anno.cubelocation = mdgrp['CUBE_LOCATION'][0]
    anno.source = mdgrp['SOURCE'][0] 

  elif annotype == annotation.ANNO_SYNAPSE:

    # Create the appropriate annotation type
    anno = annotation.AnnSynapse()

    # load the synapse specific metadata
    anno.synapse_type = mdgrp['SYNAPSE_TYPE'][0]
    anno.weight = mdgrp['WEIGHT'][0]
    anno.seeds = mdgrp['SEEDS'][:]
    anno.segments = mdgrp['SEGMENTS'] [:]

  else:
    raise Exception ("Dont support this annotation type yet")

  # now load the annotation common fields
  anno.annid = h5fh['ANNOTATION_ID'][0]
  anno.confidence = mdgrp['CONFIDENCE'][0]

  # now load the metadata common fields
  anno.status = mdgrp['STATUS'][0]
  anno.confidence = mdgrp['CONFIDENCE'][0]

  # and the key/value pairs
  fstring = cStringIO.StringIO( mdgrp['KVPAIRS'][0] )
  csvr = csv.reader(fstring, delimiter=',')
  for r in csvr:
    anno.kvpairs[r[0]] = r[1] 

  return anno


def H5GetVoxelData ( h5fh ):
  """Return the voxel data associated with the annotation
       This returns a dim3 and a numpy array"""

  # RBTODO

  return [offset, voxels]



############## Converting Annotation to HDF5 ####################

def BasetoH5 ( anno, annotype, location=None, voxels=None ):
  """Convert an annotation to HDF5 for interchange"""

  h5anno = H5Annotation ( annotype, anno.annid, location, voxels )
  
  # Set Annotation specific metadata
  h5anno.mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=anno.status )
  h5anno.mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=anno.confidence )

  # Turn our dictionary into a csv file
  fstring = cStringIO.StringIO()
  csvw = csv.writer(fstring, delimiter=',')
  csvw.writerows([r for r in anno.kvpairs.iteritems()]) 

  # User-defined metadata
  h5anno.mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())

  return h5anno


def SynapsetoH5 ( synapse, location, voxels ):
  """Convert a synapse to HDF5"""

  # First create the base object
  h5synapse = BasetoH5 ( synapse, annotation.ANNO_SYNAPSE, location, voxels )

  # Then customize
  h5synapse.mdgrp.create_dataset ( "WEIGHT", (1,), np.float, data=synapse.weight )
  h5synapse.mdgrp.create_dataset ( "SYNAPSE_TYPE", (1,), np.uint32, data=synapse.synapse_type )

  # Lists (as arrays)
  if ( synapse.seeds != [] ):
    h5synapse.mdgrp.create_dataset ( "SEEDS", (len(synapse.seeds),), np.uint32, synapse.seeds )
  else:
    h5synapse.mdgrp.create_dataset ( "SEEDS", (0,), np.uint32 )

  #  segments and segment type
  if ( synapse.segments != [] ):
    h5synapse.mdgrp.create_dataset ( "SEGMENTS", (len(synapse.segments),2), np.uint32, data=synapse.segments)
  else:
    h5synapse.mdgrp.create_dataset ( "SEGMENTS", (0,0), np.uint32 )

  return h5synapse


def SeedtoH5 ( seed ):
  """Convert a seed to HDF5"""

  # First create the base object
  h5seed = BasetoH5 ( seed, annotation.ANNO_SEED )

  # convert these  to enumerations??
  h5seed.mdgrp.create_dataset ( "PARENT", (1,), np.uint32, data=seed.parent )
  h5seed.mdgrp.create_dataset ( "CUBE_LOCATION", (1,), np.uint32, data=seed.cubelocation )
  h5seed.mdgrp.create_dataset ( "POSITION", (3,), np.uint32, data=seed.position )     
  h5seed.mdgrp.create_dataset ( "SOURCE", (1,), np.uint32, data=seed.source )     

  return h5seed

def AnnotationtoH5 ( anno ):
  """Operate polymorphically on annotations"""

  if anno.__class__ == annotation.AnnSynapse:
    return SynapsetoH5 ( anno, None, None )
  elif anno.__class__ == annotation.AnnSeed:
    return SeedtoH5 ( anno )
  elif anno.__class__ == annotation.Annotation:
    raise Exception ("(AnnotationtoH5) Can't instantiate the base class")
  else:
    raise Exception ("(AnnotationtoH5) Dont support this annotation type yet")


def main():
  """Testing main"""

  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( 'hanno' )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )

  #Load the database
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  
  location=[100,200,300]
  voxels = np.ones ( [ 100,100,100] )

  syn = annotation.AnnSynapse( )

  # common fields
  syn.annid = 36
  syn.status = 2
  syn.confidence = 0.02
  syn.kvpairs = { 'key0':'value0', 'key2':'value2' }

  # synapse fields
  syn.weight = 200.0
  syn.synapse_type = 87
  syn.seeds = [ 102, 104, 106 ]
  syn.segments = [ [112,114], [116,118] ]

  seed = annotation.AnnSeed( )

  # common fields
  seed.annid = 37
  seed.status = 3
  seed.confidence = 0.03
  seed.kvpairs = { 'key1':'value1', 'key3':'value3', 'key5':'value5' }

  # seed fields
  seed.parent=99
  seed.position=[1,3,5]
  seed.cubelocation = 73
  seed.source = 57

  h5seed = SeedtoH5 ( seed )
  h5syn  = SynapsetoH5 ( syn, location, voxels )

  outsyn = H5toAnnotation ( h5syn.h5fh )
  outsyn.store(annodb)

  outseed = H5toAnnotation ( h5seed.h5fh )
  outseed.store(annodb)

  readsyn = annotation.AnnSynapse()
  readseed = annotation.AnnSeed()

  readsyn.retrieve(36, annodb)
  readseed.retrieve(37, annodb)

  h5seed = SeedtoH5 ( readseed )
  h5syn  = SynapsetoH5 ( readsyn, location, voxels )

  lastsyn = H5toAnnotation ( h5syn.h5fh )
  lastseed = H5toAnnotation ( h5seed.h5fh )


  print "Synapse start:"
  pprint(vars(syn)) 

  print "Synapse end data:"
  pprint(vars(lastsyn)) 

  print "Seed start:"
  pprint(vars(seed)) 

  print "Seed end data:"
  pprint(vars(lastseed)) 


if __name__ == "__main__":
  main()





