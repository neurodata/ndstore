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

# TODO implement data and author
#  support missing values
# suport untyped files

"""The HDF5 format currently looks like:

/  (Root) group:

ANNOTATION_TYPE (int)
ANNOTATION_ID (int)
XYZOFFSET ( int[3] optional defined with volume )
VOLUME ( int32 3-d array optional defined with XYZOFFSET )
VOXELS ( int32[][3] optional if defined XYZOFFSET and VOLUME must be empty ) 

METADATA group;

 # metadata for all annotations
 CONFIDENCE (float)
 STATUS (int) 
 KVPAIRS   (string containing csv pairs)
 AUTHOR ( string ) 

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

  def __init__( self, annotype, annoid, anndata=None, xyzoffset=None):
    """Create an HDF5 file and simple structure
      calls with data as a list of voxels and location == None for voxel lists
      call with data as an array of data and xyzoffset for a volume
     """

    # Create an in-memory HDF5 file
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.h5fh = h5py.File ( self.tmpfile.name )

    # Annotation type
    self.h5fh.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )
    self.h5fh.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=annoid )
    
    # Create a metadata group
    self.mdgrp = self.h5fh.create_group ( "METADATA" ) 

    # who is the author

    # Volume of data if xyzoffset defined
    if xyzoffset != None:
      self.h5fh.create_dataset ( "XYZOFFSET", (3,), np.uint32, anndata=xyzoffset )     
      self.h5fh.create_dataset ( "VOLUME", anndata.shape, np.uint32, compression='gzip', data=anndata )
    # List of voxels if anndata defined and not xyzoffset
    elif anndata != None:
      self.h5fh.create_dataset ( "VOXELS", anndata.shape, np.uint32, compression='gzip', data=anndata )

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
  if h5fh.get('ANNOTATION_TYPE'):
    annotype = h5fh['ANNOTATION_TYPE'][0]
  else:
    annotype = annotation.ANNO_NOTYPE

  # And get the metadata group
  mdgrp = h5fh.get('METADATA')

  if annotype == annotation.ANNO_SEED:

    # Create the appropriate annotation type
    anno = annotation.AnnSeed()

    # Load metadata if it exists
    if mdgrp:
      # load the seed specific metadata
      if mdgrp.get('PARENT'):
        anno.parent = mdgrp['PARENT'][0]
      if mdgrp.get('POSITION'):
        anno.position = mdgrp['POSITION'][:]
      if mdgrp.get('CUBE_LOCATION'):
        anno.cubelocation = mdgrp['CUBE_LOCATION'][0]
      if mdgrp.get('SOURCE'):
        anno.source = mdgrp['SOURCE'][0] 

  elif annotype == annotation.ANNO_SYNAPSE:
    
    # Create the appropriate annotation type
    anno = annotation.AnnSynapse()

    # Load metadata if it exists
    if mdgrp:
      # load the synapse specific metadata
      if mdgrp.get('SYNAPSE_TYPE'):
        anno.synapse_type = mdgrp['SYNAPSE_TYPE'][0]
      if mdgrp.get('WEIGHT'):
        anno.weight = mdgrp['WEIGHT'][0]
      if mdgrp.get('SEEDS') and len(mdgrp['SEEDS'])!=0:
        anno.seeds = mdgrp['SEEDS'][:]
      if mdgrp.get('SEGMENTS') and len(mdgrp['SEGMENTS'])!=0:
        anno.segments = mdgrp['SEGMENTS'] [:]

  # No special action if it's a no type
  elif annotype == annotation.ANNO_NOTYPE:
    # Just create a generic annotation object
    anno = annotation.Annotation()

  else:
    raise Exception ("Dont support this annotation type yet")

  # now load the annotation common fields
  if h5fh.get('ANNOTATION_ID'):
    anno.annid = h5fh['ANNOTATION_ID'][0]

  if mdgrp:
    # now load the metadata common fields
    if mdgrp.get('STATUS'):
      anno.status = mdgrp['STATUS'][0]
    if mdgrp.get('CONFIDENCE'):
      anno.confidence = mdgrp['CONFIDENCE'][0]
    if mdgrp.get('AUTHOR'):
      anno.author = mdgrp['AUTHOR'][0]

    # and the key/value pairs
    if mdgrp.get('KVPAIRS'):
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

def BasetoH5 ( anno, annotype, anndata=None, xyzoffset=None ):
  """Convert an annotation to HDF5 for interchange"""

  h5anno = H5Annotation ( annotype, anno.annid, anndata, xyzoffset )

  # Set Annotation specific metadata
  h5anno.mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=anno.status )
  h5anno.mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=anno.confidence )
  h5anno.mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=anno.author )

  # Turn our dictionary into a csv file
  fstring = cStringIO.StringIO()
  csvw = csv.writer(fstring, delimiter=',')
  csvw.writerows([r for r in anno.kvpairs.iteritems()]) 

  # User-defined metadata
  h5anno.mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())

  return h5anno


def SynapsetoH5 ( synapse, anndata, xyzoffset ):
  """Convert a synapse to HDF5"""

  # First create the base object
  h5synapse = BasetoH5 ( synapse, annotation.ANNO_SYNAPSE, anndata, xyzoffset )

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
  h5seed.mdgrp.create_dataset ( "SOURCE", (1,), np.uint32, data=seed.source )     
  if seed.position != [None, None, None]:
    h5seed.mdgrp.create_dataset ( "POSITION", (3,), np.uint32, data=seed.position )     

  return h5seed

def AnnotationtoH5 ( anno ):
  """Operate polymorphically on annotations"""

  if anno.__class__ == annotation.AnnSynapse:
    return SynapsetoH5 ( anno, None, None )
  elif anno.__class__ == annotation.AnnSeed:
    return SeedtoH5 ( anno )
  elif anno.__class__ == annotation.Annotation:
    return BasetoH5 ( anno, annotation.ANNO_NOTYPE, None, None )
  else:
    raise Exception ("(AnnotationtoH5) Dont support this annotation type yet")


def main():
  """Testing main"""

  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( 'hanno' )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )

  #Load the database
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  
  xyzoffset=[100,200,300]
  anndata = np.ones ( [ 100,100,100] )

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





