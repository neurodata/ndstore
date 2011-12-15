##############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import cStringIO
from PIL import Image
import zlib

import empaths
import dbconfig
import zindex

#
#  AnnotateCube: manipulate the in-memory data representation of the 3-d cube of data
#    that contains annotations.
#

# RBTODO testing in B and W.  Change to 24 bit.

class AnnotateCube:

  # Constructor 
  #
  #  Express cubesize in [ x,y,z ]
  def __init__(self, cubesize):
    """Create empty array of cubesize"""

    # cubesize is in z,y,x for interactions with tile/image data
#    self.zdim, self.ydim, self.xdim =  self.cubesize = [ cubesize[2],cubesize[1],cubesize[0] ]
    #RBTODO for testing
    self.zdim, self.ydim, self.xdim =  self.cubesize = [ 4,4,4 ]

  # Constructor 
  def __del__(self):
    """Destructor"""
    pass

  # create an all zeros cube
  def zeros ( self ):
    """Create a cube of all 0"""
    self.data = np.zeros ( self.cubesize, dtype=np.uint32 )

  # load the object from a Numpy pickle
  def fromNPZ ( self, pandz ):
    """Load the cube from a pickled and zipped blob"""
    try:
      newstr = zlib.decompress ( pandz[:] )
      newfobj = cStringIO.StringIO ( newstr )
      self.data = np.load ( newfobj )
    except:
      print "Unpickle and unZip.  What did I catch?"
      assert 0


  # return a numpy pickle to be stored in the database
  def toNPZ ( self ):
    """Pickle and zip the object"""
    try:
      # Create the compressed cube
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, self.data )
      return  zlib.compress (fileobj.getvalue())
    except:
      print "Picle and Zip.  What did I catch?"
      assert 0


  # Add annotations
  #
  #  We are mostly going to assume that annotations are non-overlapping.  When they are,
  #  we are going to be less than perfectly efficient.
  #  
  #  Returns a list of exceptions  
  #
  def addEntity ( self, annid, offset, locations ):
    """Add annotation by a list of locations"""

#  For now first label for a voxel wins

    exceptions = []

    # xyz coordinates get stored as zyx to be more
    #  efficient when converting to images
    for voxel in locations:
  #    if ( self.data [ voxel[2], voxel[1], voxel[0] ] == 0 ):
      if ( 1 ):
        self.data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0] ] = annid
      else:
        exceptions.append ( voxel )
  
    return exceptions

  #
  #  addCube -- from another cube to this cube
  #    the nparray is in x,y,z and the self is in z,y,x
  #
  def addCube ( self, nparray, corner ):
    """Add data from an nparray"""
 
    npasize = nparray.shape

    # Check that it is a legal assignment within bounds
    assert self.xdim >= 0 and self.xdim <= npasize[0] + corner[0]
    assert self.ydim >= 0 and self.ydim <= npasize[1] + corner[1]
    assert self.zdim >= 0 and self.zdim <= npasize[2] + corner[2]

    tmparray = nparray.transpose()

    self.data [ corner[2]:corner[2]+npasize[2],\
                corner[1]:corner[1]+npasize[1],\
                corner[0]:corner[0]+npasize[0] ] = tmparray[:,:,:]


# end AnnotateCube

