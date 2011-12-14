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
  def __init__(self):
    """Create empty array of cubesize"""

    # cubesize is in z,y,x for interactions with tile/image data
    self.zdim, self.ydim, self.xdim =  self.cubesize = [ cubesize[2],cubesize[1],cubesize[0] ]
    self.data = np.zeros ( self.cubesize, dtype=np.uint32 )

  # Constructor 
  def __del__(self):
    """Destructor"""
    pass

  # load the object from a Numpy pickle
  def fromNPZ (self, pandz ):
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

  # Add annotation  by locations
  def addItem ( self, annid, locations ):
    """Add annotation by a list of locations"""
    for voxel in locations:
      self.data [ voxel[2], voxel[1], voxel[0] ] = annid
  

  #
  #  addCube -- from another cube to this cube
  #    the nparray is in x,y,z and the self is in z,y,x
  #
  def addCube ( self, nparray, corner ):
    """Add data from an nparray"""

    assert(0)

    # RB not tested.  Is x,y,z -> z,y,x correct
    npasize = nparray.shape

    # Check that it is a legal assignment within bounds
    assert self.xdim >= 0 and self.xdim <= npasize[0] + corner[0]
    assert self.ydim >= 0 and self.ydim <= npasize[1] + corner[1]
    assert self.zdim >= 0 and self.zdim <= npasize[2] + corner[2]

    temparray = nparray.transpose()

    self.data [ corner[2]:corner[2]+npasize[2],\
                corner[1]:corner[1]+npasize[1],\
                corner[0];corner[0]+npasize[0] ] = tmparray[:,:,:]

  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (xdim,ydim), self.data[0,:,:].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( fileobj, "PNG" )
  

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (xdim,zdim), self.data[:,0,:].flatten(), 'raw', 'L', 0, 1 ) 
    #TODO if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [xdim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )
  

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (ydim,zdim), self.data[:,:,0].flatten(), 'raw', 'L', 0, 1 ) 
    #TODO if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [ydim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )


  #
  # Trim off the excess data
  #  translate xyz -> zyx
  #
  def cutout ( self, xoffset, xsize, yoffset, ysize, zoffset, zsize ):
    """Trim off the excess data"""
    self.data = self.data [ zoffset:zoffset+zsize, yoffset:yoffset+ysize, xoffset:xoffset+xsize ]
  
# end AnnotateCube

