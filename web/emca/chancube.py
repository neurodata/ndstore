import numpy as np
import zindex
from libtiff import TIFF
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
  # Extract data from the cube and write out TIFF files.
  #
  def cubeToTIFFs ( self, prefix ):
    """Move data from tiled files to array"""  

    zdim,ydim,xdim = self.data.shape
    for k in range(zdim):
      tif = TIFF.open(prefix + str(k) + ".tif", mode="w")
      tif.write_image( self.data[k,:,:] )
      tif.close()

  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[0,:,:] )
    tif.close()
  

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[:,0,:] )
    tif.close()

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    zdim,ydim,xdim = self.data.shape
    tif = TIFF.open(fileobj, mode="w")
    tif.write_image( self.data[:,:,0] )
    tif.close()

# end BrainCube

