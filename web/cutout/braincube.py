##############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import tiles
import zindex
from PIL import Image

#
#  BrainCube: manipulate the in-memory data representation of the 3-d cube of data
#    includes loading, export, read and write routines
#
#  All the interfaces to this class are in x,y,z order
#  Cube data goes in z,y,x order by virtue of using fortran ordered Numpy arrays
#    this is compatible with images and more efficient?
#
class BrainCube:

  # Constructor 
  def __init__(self, cubesize=[64,64,64]):
    """Create empty array of cubesize"""

    # data stored in Fortran order for conversion/compatibility with images
    self.xdim, self.ydim, self.zdim =  self.cubesize = [ cubesize[0],cubesize[1],cubesize[2] ]
    self.data = np.zeros ( self.cubesize, dtype=np.uint8, order='F' )

  # CubefromFiles
  def cubeFromFiles ( self, corner, tilestack ):
    """Initialize the cube from files.  Specify low x,y,z corner."""
    return tilestack.tilesToCube ( corner, self ) 

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
    
    self.data [ xoffset:xoffset+other.xdim,\
                yoffset:yoffset+other.ydim,\
                zoffset:zoffset+other.zdim ]\
            = other.data [:,:,:]
    

  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

    xdim,ydim,zdim = self.data.shape
    print self.data
    print self.data[:,:,0].flatten()
    outimage = Image.frombuffer ( 'L', (xdim,ydim), self.data[:,:,0].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( fileobj, "PNG" )
  

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, zscale, fileobj  ):

    xdim,ydim,zdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (xdim,zdim), self.data[:,0,:].flatten(), 'raw', 'L', 0, 1 ) 
    #TODO if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [xdim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )
  

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, zscale, fileobj  ):

    xdim,ydim,zdim = self.data.shape
    outimage = Image.frombuffer ( 'L', (ydim,zdim), self.data[0,:,:].flatten(), 'raw', 'L', 0, 1 ) 
    #TODO if the image scales to 0 pixels it don't work
    newimage = outimage.resize ( [ydim, int(zdim*zscale)] )
    newimage.save ( fileobj, "PNG" )

  #
  # Trim off the excess data
  #  translate xyz -> zyx
  #
  def trim ( self, xoffset, xsize, yoffset, ysize, zoffset, zsize ):
    """Trim off the excess data"""

    self.data = self.data [ xoffset:xoffset+xsize, yoffset:yoffset+ysize, zoffset:zoffset+zsize ]
  
# end BrainCube

