##############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import array
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

class AnnotateCube:

  # Constructor 
  #
  #  Express cubesize in [ x,y,z ]
  def __init__(self, cubesize):
    """Create empty array of cubesize"""

    # cubesize is in z,y,x for interactions with tile/image data
    self.zdim, self.ydim, self.xdim = self.cubesize = [ cubesize[2],cubesize[1],cubesize[0] ]
  
    # variable that describes when a cube is created from zeros
    #  rather than loaded from another source
    self._newcube = False

  # Constructor 
  def __del__(self):
    """Destructor"""
    pass

  # was the cube created from zeros?
  def fromZeros ( self ):
    """Determine if the cube was created from all zeros?"""
    if self._newcube == True:
      return True
    else: 
      return False

  # create an all zeros cube
  def zeros ( self ):
    """Create a cube of all 0"""
    self._newcube = True
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

    self._newcube = False


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
  def annotate ( self, annid, offset, locations ):
    """Add annotation by a list of locations"""

  #  For now first label for a voxel wins

    exceptions = []

    # xyz coordinates get stored as zyx to be more
    #  efficient when converting to images
    for voxel in locations:
      #  label unlabeled voxels
      if ( self.data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] == 0 ):
        self.data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0] ] = annid

      # already labelled voxels are exceptions, unless they are the same value
      elif (self.data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] != annid ):
        exceptions.append ( voxel )

      #RBTODO remove this after testing
      else:
        print "Not an exception"
  
#RBTODO remove
    if len(exceptions) != 0:
      print exceptions

    return exceptions


  # arrayUpdate
  #
  #  Update the existing cube with these identifiers specified in this cube.
  #
  #  Returns a list of exceptions  
  #
  def arrayUpdate ( self, npdata ):
    """Update the cube with an array of the same size"""

    assert self.data.shape == npdata.shape

    for z in range ( self.data.shape[0] ):
      for y in range ( self.data.shape[1] ):
        for x in range ( self.data.shape[2] ):

          if npdata[z,y,x] != 0:
            if self.data[z,y,x] == 0:
              self.data[z,y,x] = npdata[z,y,x]
#RBTODO these are the exceptions you need to deal with
            else:
              self.data[z,y,x] = npdata[z,y,x]



  #
  #  addData -- from another cube to this cube
  #
  def addData ( self, other, index ):
    """Add data to a larger cube from a smaller cube"""

    # Check that it is a legal assignment   
    #  aligned and within bounds
    assert self.xdim % other.xdim == 0
    assert self.ydim % other.ydim == 0
    assert self.zdim % other.zdim == 0

    assert (index[0]+1)*other.xdim <= self.xdim
    assert (index[1]+1)*other.ydim <= self.ydim
    assert (index[2]+1)*other.zdim <= self.zdim

    xoffset = index[0]*other.xdim
    yoffset = index[1]*other.ydim
    zoffset = index[2]*other.zdim

    self.data [ zoffset:zoffset+other.zdim,\
                yoffset:yoffset+other.ydim,\
                xoffset:xoffset+other.xdim ]\
            = other.data [:,:,:]

  #
  # Trim off the excess data
  #
  def trim ( self, xoffset, xsize, yoffset, ysize, zoffset, zsize ):
    """Trim off the excess data"""
    self.data = self.data [ zoffset:zoffset+zsize, yoffset:yoffset+ysize, xoffset:xoffset+xsize ]

  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

#    zdim,ydim,xdim = self.data.shape
#    outimage = Image.frombuffer ( 'L', (xdim,ydim), self.data[0,:,:].flatten(), 'raw', 'L', 0, 1 )
#    outimage.save ( fileobj, "PNG" )

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ ydim, xdim ], dtype=np.uint32 )

    for y in range(ydim):
      for x in range(xdim):
        if self.data[0,y,x] != 0:
          imagemap[y,x] = 0x80000000 + ( self.data[0,y,x] & 0xFF )
    
    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), imagemap, 'raw', 'RGBA', 0, 1 )
    outimage.save ( fileobj, "PNG" )

# end AnnotateCube

