import numpy as np
import urllib2
import tempfile
import h5py

#
#  hdf5anno.py
#
#  Demonstration of packaging and HDF5 and metadata 
#  for synapses and seeds.
#

class HDF5Annotation:
  """Class to hold a set of annotations stored in an HDF5 file.
      This is a dense represenation of seeds and synapses."""

  # Constants for lists
  self.MAX_SEEDS = 128
  self.MAX_SEGMENTS = 128

  def __init__( self, annotype, dim, voxdata=None ):
    """Create an HDF5 file and directory structure
        dim -- specifies the size of the data as [x,y,z]."""

    # Create an in-memory HDF5 file
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.fh5out = h5py.File ( tmpfile.name )

    # Annotation type
    # RTODO Convert the np.uint32 to ANNO_TYPE_ENUM
    self.fh5out.create_dataset ( "ANNOTATION_TYPE", 1, np.uint32, data=annotype )

    # Zeroed data if not none
    if voxdata == None:
      voxdata = np.zeros ( dim ) 

    # Zero'ed voxel data.  Treat like a Numpy array
    self.voxels = self.fh5out.create_dataset ( "VOXEL_DATA", dim, np.uint32, compression='gzip', data=voxdata )

    # Create a metadata group
    self.mdgrp = self.fh5out.create_group ( "METADATA" ) 

    # and the metadata fields
    self._conf = self.mdgrp.create_dataset ( "CONFIDENCE", (1), np.float, data=0.0 )
    self._wght = self.mdgrp.create_dataset ( "WEIGHT", (1), np.float, data=0.0 )

    # RBTODO convert these  to enumerations
    self._stat = self.mdgrp.create_dataset ( "STATUS", (1), np.uint32, data=0 )
    self._syntype = self.mdgrp.create_dataset ( "SYNAPSE_TYPE", (1), np.uint32, data=0 )
    self._segtype = self.mdgrp.create_dataset ( "SEGMENT_TYPE", (1), np.uint32, data=0 )

    # Lists (as arrays)
    self._seeds = self.mdgrp.create_dataset ( "SEEDS", {self.MAX_SEEDS}, np.uint32 )
    self._segs = self.mdgrp.create_dataset ( "SEGMENTS", {self.MAX_SEGMENTS}, np.uint32 )
    # User-defined metadata
    self._userdef = self.mdgrp.create_dataset ( "USER_DEFINED", (1), dtype=h5py.special_dtype(vlen=str))



    
  def __del__ ( self ):
    """Destructor"""
    fh5out.close()

  def fileRead():
    """Return a file read stream to be transferred as put data"""
    self.tmpfile.seek(0)
    return self.tmpfile.read()

  """Accessors and modifiers"""
  def setConfidence ( self, confidence ):
    self._conf = confidence

  def getConfidence ( self ):
    return self._conf

  def setWeight ( self, weight ):
    self._wght = weight

  def getWeight ( self ):
    return self._wght

  def setStatus ( self, status ):
    self._stat = status

  def getStatus ( self ):
    return self._stat

  def setSynapseType ( self, syn_type ):
    self._syntype = syn_type

  def getSynapseType ( self ):
    return self._syntype

  def setSegmentType ( self, seg_type ):
    self._segtype = seg_type

  def getSegmentType ( self ):
    return self._segtype





    

def addSeed ( 



# Get cube in question
try:
#  url = "http://0.0.0.0:8080/hdf5/2/0,1000/0,1000/0,80/global/"
  url = "http://openconnectomeproject.org/cutout/hayworth5nm/hdf5/0/2000,3000/2000,3000/50,70/global/"
  f = urllib2.urlopen ( url )
except URLError:
  print "Failed to get URL", url
  assert 0

# This feels like one more copy than is needed
tmpfile = tempfile.NamedTemporaryFile ( )
tmpfile.write ( f.read() )
print tmpfile.tell()
h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )
print h5f.keys()
cube = h5f['cube']

# Write out the cube as files
cubeToPNGs ( cube, "/tmp/t" )
