import numpy as np
import array
import cStringIO
from PIL import Image
import zlib

import empaths
import dbconfig
import zindex

from ann_cy import annotate_cy

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
      print "Pickle and Zip.  What did I catch?"
      assert 0


  # Add annotations
  #
  #  We are mostly going to assume that annotations are non-overlapping.  When they are,
  #  we are going to be less than perfectly efficient.
  #  
  #  Returns a list of exceptions  
  #
  def annotate ( self, annid, offset, locations, conflictopt ):
    """Add annotation by a list of locations"""

    # the cython optimized version of this function.
    return annotate_cy ( self.data, annid, offset, np.array(locations, dtype=np.uint32), conflictopt )
  

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
                xoffset:xoffset+other.xdim]\
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

    zdim,ydim,xdim = self.data.shape

    imagemap = np.zeros ( [ ydim, xdim ], dtype=np.uint32 )

    # recolor the pixels for visualization
    vecfunc_recolor = np.vectorize ( lambda x:  np.uint32(0) if x == 0 else np.uint32(0x80000000+(x&0xFF)))
    imagemap = vecfunc_recolor ( self.data[:,:,:] )
    imagemap = imagemap.reshape ( ydim, xdim )

    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), imagemap, 'raw', 'RGBA', 0, 1 )
    outimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def xzSlice ( self, scale, fileobj ):

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ zdim, xdim ], dtype=np.uint32 )

    # recolor the pixels for visualization
    vecfunc_recolor = np.vectorize ( lambda x:  np.uint32(0) if x == np.uint32(0) else np.uint32(0x80000000+(x&0xFF)))
    imagemap = vecfunc_recolor ( self.data[:,:,:] )
    imagemap = imagemap.reshape ( zdim, xdim )

    outimage = Image.frombuffer ( 'RGBA', (xdim,zdim), imagemap, 'raw', 'RGBA', 0, 1 )
    newimage = outimage.resize ( [xdim, int(zdim*scale)] )
    newimage.save ( fileobj, "PNG" )

  #
  # Create the specified slice (index) at filename
  #
  def yzSlice ( self, scale, fileobj ):

    zdim,ydim,xdim = self.data.shape
    imagemap = np.zeros ( [ zdim, ydim ], dtype=np.uint32 )

    # recolor the pixels for visualization
    vecfunc_recolor = np.vectorize ( lambda x:  np.uint32(0) if x == 0 else np.uint32(0x80000000+(x&0xFF)))
    imagemap = vecfunc_recolor ( self.data[:,:,:] )
    imagemap = imagemap.reshape ( zdim, ydim )

    outimage = Image.frombuffer ( 'RGBA', (ydim,zdim), imagemap, 'raw', 'RGBA', 0, 1 )
    newimage = outimage.resize ( [ydim, int(zdim*scale)] )
    newimage.save ( fileobj, "PNG" )


  def overwrite ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    assert ( self.data.shape == annodata.shape )
    vector_func = np.vectorize ( lambda a,b: b if b!=0 else a ) 
    self.data = vector_func ( self.data, annodata ) 

  def preserve ( self, annodata ):
    """Get's a dense voxel region and overwrites all non-zero values"""

    assert ( self.data.shape == annodata.shape )
    vector_func = np.vectorize ( lambda a,b: b if b!=0 and a==0 else a ) 
    self.data = vector_func ( self.data, annodata ) 

# end AnnotateCube

