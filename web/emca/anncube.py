import numpy as np
import array
import cStringIO
from PIL import Image
import zlib

import empaths
import dbconfig
import zindex
from cube import Cube

from emca_cy import annotate_cy
from emca_cy import shave_cy
from emca_cy import recolor_cy

#
#  AnnotateCube: manipulate the in-memory data representation of the 3-d cube of data
#    that contains annotations.  
#

class AnnotateCube(Cube):

  # Constructor 
  #
  #  Express cubesize in [ x,y,z ]
  def __init__(self, cubesize):
    """Create empty array of cubesize"""

    # call the base class constructor
    Cube.__init__( self, cubesize )

    # variable that describes when a cube is created from zeros
    #  rather than loaded from another source
    self._newcube = False


  # get the value by x,y,z coordinate
  def getVoxel ( self, voxel ):
    """Return the value at the voxel specified as [x,y,z]"""
    return self.data [ voxel[2], voxel[1], voxel[0] ]
  

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


  # Add annotations
  #
  #  We are mostly going to assume that annotations are non-overlapping.  When they are,
  #  we are going to be less than perfectly efficient.
  #  
  #  Returns a list of exceptions  
  #
  #  Exceptions are uint8 to keep them small.  Max cube size is 256^3.
  #
  def annotate ( self, annid, offset, locations, conflictopt ):
    """Add annotation by a list of locations"""

    # the cython optimized version of this function.
    return annotate_cy ( self.data, annid, offset, np.array(locations, dtype=np.uint32), conflictopt )

  def shave ( self, annid, offset, locations ):
    """Remove annotation by a list of locations"""

    # the cython optimized version of this function.
    return shave_cy ( self.data, annid, offset, np.array(locations, dtype=np.uint32))
  

  #
  # Create the specified slice (index) at filename
  #
  def xySlice ( self, fileobj ):

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ ydim, xdim ], dtype=np.uint32 )

    # false color redrawing of the region
    recolor_cy ( self.data.reshape((imagemap.shape[0],imagemap.shape[1])), imagemap )

    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), imagemap, 'raw', 'RGBA', 0, 1 )
    outimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, scale, fileobj ):

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ zdim, xdim ], dtype=np.uint32 )

    # false color redrawing of the region
    recolor_cy ( self.data.reshape((imagemap.shape[0],imagemap.shape[1])), imagemap )

    outimage = Image.frombuffer ( 'RGBA', (xdim,zdim), imagemap, 'raw', 'RGBA', 0, 1 )
    newimage = outimage.resize ( [xdim, int(zdim*scale)] )
    newimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, scale, fileobj ):

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ zdim, ydim ], dtype=np.uint32 )

    # false color redrawing of the region
    recolor_cy ( self.data.reshape((imagemap.shape[0],imagemap.shape[1])), imagemap )

    outimage = Image.frombuffer ( 'RGBA', (ydim,zdim), imagemap, 'raw', 'RGBA', 0, 1 )
    newimage = outimage.resize ( [ydim, int(zdim*scale)] )
    newimage.save ( fileobj, "PNG" )


  def overwrite ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    vector_func = np.vectorize ( lambda a,b: b if b!=0 else a ) 
    self.data = vector_func ( self.data, annodata ) 

  def preserve ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    vector_func = np.vectorize ( lambda a,b: b if b!=0 and a==0 else a ) 
    self.data = vector_func ( self.data, annodata ) 

  def exception ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    # get all the exceptions
    # not equal and both annotated
    exdata = ((self.data-annodata)*self.data*annodata!=0) * annodata 

    # then annotate to preserve 
    vector_func = np.vectorize ( lambda a,b: b if b!=0 and a==0 else a ) 
    self.data = vector_func ( self.data, annodata ) 

    # return the list of exceptions ids and the exceptions
    return exdata

  def shaveDense ( self, annodata ):
    """Remove the specified voxels from the annotation"""

    # get all the exceptions that are equal to the annid in both datasets
    shavedata = ((self.data-annodata)==0) * annodata 

    # find all shave requests that don't match the dense data
    exdata = (self.data != annodata) * annodata

    # then shave 
    vector_func = np.vectorize ( lambda a,b: 0 if b!=0 else a ) 
    self.data = vector_func ( self.data, shavedata ) 

    # return the list of exceptions ids and the exceptions
    return exdata

# end AnnotateCube

