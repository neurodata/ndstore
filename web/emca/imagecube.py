import numpy as np
import zindex
from PIL import Image

from cube import Cube

#
#  ImageCube: manipulate the in-memory data representation of the 3-d cube of data
#    includes loading, export, read and write routines
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order this is compatible with images and more efficient?
#
class ImageCube8(Cube):

  # Constructor 
  def __init__(self, cubesize=[64,64,64]):
    """Create empty array of cubesize"""

    # call the base class constructor
    Cube.__init__(self,cubesize)
    # note that this is self.cubesize (which is transposed) in Cube
    self.data = np.zeros ( self.cubesize, dtype=np.uint8 )


  # CubefromFiles
  def cubeFromFiles ( self, corner, tilestack ):
    """Initialize the cube from files.  Specify low x,y,z corner."""
    return tilestack.tilesToCube ( corner, self ) 

    
  #
  # Extract data from the cube and write out PNG files.
  #
  def cubeToPNGs ( self, prefix ):
    """Move data from tiled files to array"""  

    zdim,ydim,xdim = self.data.shape
    for k in range(zdim):
      outimage = Image.frombuffer ( 'L', (xdim,ydim), self.data[k,:,:].flatten(), 'raw', 'L', 0, 1 ) 
      outimage.save ( prefix + str(k) + ".png", "PNG" )

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
    #if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [xdim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )
  

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (ydim,zdim), self.data[:,:,0].flatten(), 'raw', 'L', 0, 1 ) 
    #if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [ydim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )


#
#  ImageCube16: manipulate the in-memory data representation of the 3-d cube 
#    includes loading, export, read and write routines
#
#  This sub-class is for 16 bit data 
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order this is compatible with images and more efficient?
#
class ImageCube16(Cube):

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
  def xzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'I;16', (xdim,zdim), self.data[:,0,:].flatten(), 'raw', 'I;16', 0, 1) 
    outimage = outimage.point(lambda i:i*(1./256)).convert('L')
    outimage.save ( fileobj, "PNG" )


  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'I;16', (ydim,zdim), self.data[:,:,0].flatten(), 'raw', 'I;16', 0, 1) 
    outimage = outimage.point(lambda i:i*(1./256)).convert('L')
    outimage.save ( fileobj, "PNG" )

# end BrainCube

