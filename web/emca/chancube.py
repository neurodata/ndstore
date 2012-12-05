import numpy as np
import zindex
from libtiff import TIFF
from PIL import Image
from cube import Cube

#
#  ChanCube: manipulate the in-memory data representation of the 3-d cube 
#    includes loading, export, read and write routines
#
#  This sub-class is for 16 bit channel data 
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order this is compatible with images and more efficient?
#
class ChanCube(Cube):

  # Constructor 
  def __init__(self, cubesize=[64,64,64]):
    """Create empty array of cubesize"""

    # call the base class constructor
    Cube.__init__(self,cubesize)
    # note that this is self.cubesize (which is transposed) in Cube
    self.data = np.zeros ( self.cubesize, dtype=np.uint16 )


  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

# This works for 16-> conversions
    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'I;16', (xdim,ydim), self.data[0,:,:].flatten(), 'raw', 'I;16', 0, 1) 
    outimage = outimage.point(lambda i:i*(1./256)).convert('L')
    outimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def xyTiff ( self, fileobj ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[0,:,:] )
    tif.close()


  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'I;16', (xdim,zdim), self.data[:,0,:].flatten(), 'raw', 'I;16', 0, 1) 
    outimage = outimage.point(lambda i:i*(1./256)).convert('L')
    outimage.save ( fileobj, "PNG" )


  #
  # Create the specified slice (index) at filename
  #
  def xzTiff ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[:,0,:] )
    tif.close()

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'I;16', (ydim,zdim), self.data[:,:,0].flatten(), 'raw', 'I;16', 0, 1) 
    outimage = outimage.point(lambda i:i*(1./256)).convert('L')
    outimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def yzTiff ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[:,:,0] )
    tif.close()

# end BrainCube

