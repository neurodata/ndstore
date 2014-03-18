import numpy as np
import zindex
from PIL import Image

from cube import Cube

#
#  BitMapCube: manipulate the in-memory data representation of the 3-d cube of data
#    includes loading, export, read and write routines
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order this is compatible with images and more efficient?
#
class MaskCube(Cube):

  # Constructor 
  def __init__(self, cubesize=[64,64,64]):
    """Create empty array of cubesize"""

    # call the base class constructor
    Cube.__init__(self,cubesize)
    # note that this is self.cubesize (which is transposed) in Cube
    self.data = np.zeros ( self.cubesize, dtype=np.uint8 )


  def _pack (self, unpacked ):
    """Pack an array into a bitmap"""
    pass

  def _unpack ( self ):
    """Unpack a bitmap into an array"""
    pass
    #return unpacked

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


  # load the object from a Numpy pickle
  def fromNPZ ( self, pandz ):
    """Load the cube from a pickled and zipped blob"""

    super(MaskCube,self).fromNPZ(pandz)
    self.data = np.unpackbits ( self.data )


  # return a numpy pickle to be stored in the database
  def toNPZ ( self ):
    """Pickle and zip the object"""

    self.data = np.packbits ( self.data )
    super(MaskCube,self).toNPZ()




