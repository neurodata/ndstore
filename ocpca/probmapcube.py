import numpy as np
import zindex
from PIL import Image

from cube import Cube

#
#  ProbMapCube: manipulate the in-memory data representation of the 3-d cube of data
#    includes loading, export, read and write routines
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order this is compatible with images and more efficient?
#
class ProbMapCube32(Cube):

  # Constructor 
  def __init__(self, cubesize=[64,64,64]):
    """Create empty array of cubesize"""

    # call the base class constructor
    Cube.__init__(self,cubesize)
    # note that this is self.cubesize (which is transposed) in Cube
    self.data = np.zeros ( self.cubesize, dtype=np.float32 )

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
    self.data = np.zeros ( self.cubesize, dtype=np.float32 )

  def overwrite ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    vector_func = np.vectorize ( lambda a,b: b if b!=0.0 else a ) 
    self.data = vector_func ( self.data, annodata ) 


  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

    # translate the 0-1 map down to to 256 value
    imgdata = np.uint8(self.data*256)

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (xdim,ydim), imgdata[0,:,:].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, zscale, fileobj  ):

    # translate the 0-1 map down to to 256 value
    imgdata = np.uint8(self.data*256)

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (xdim,zdim), imgdata[:,0,:].flatten(), 'raw', 'L', 0, 1 ) 
    #if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [xdim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    # translate the 0-1 map down to to 256 value
    imgdata = np.uint8(self.data*256)

    zdim,ydim,xdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (ydim,zdim), imgdata[:,:,0].flatten(), 'raw', 'L', 0, 1 ) 
    #if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [ydim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )
