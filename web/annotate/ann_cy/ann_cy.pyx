import numpy as np
cimport numpy as np

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

def annotate_cy ( np.ndarray[DTYPE_t, ndim=3] data, int annid, offset, np.ndarray[DTYPE_t, ndim=2] locations, conflictopt ):
  """Add annotation by a list of locations"""

# RBTODO do need to implement exceptions correctly

  cdef int xoffset
  cdef int yoffset
  cdef int zoffset

  xoffset, yoffset, zoffset = offset

  exceptions = []

  # xyz coordinates get stored as zyx to be more
  #  efficient when converting to images
  for i in range (len(locations)):
    voxel = locations[i]
    #  label unlabeled voxels
    if ( data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] == 0 ):
         data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0] ] = annid

    # already labelled voxels are exceptions, unless they are the same value
    elif (data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] != annid ):
      # O is for overwrite
      if conflictopt == 'O':
        data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0] ] = annid
      # P preserves the existing content
      elif conflictopt == 'P':
        pass
      # E creates exceptions
#      elif conflictopt == 'E':
#        exceptions.append ( voxel )
      else:
        print ( "Improper conflict option selected.  Option = ", conflictopt  )
        assert 0

  return exceptions


cdef int getAnnValue ( int value00, int value01, int value10, int value11 ):
  """Determine the annotation value at the next level of the hierarchy from a 2x2"""

  # The following block of code places the majority annotation into value
  # start with 00
  cdef int value = value00

  # put 01 in if not 00
  # if they are the same, that's fine
  if value == 0:
    value = value01

  if value10 != 0:
    if value == 0:
      value = value10
    # if this value matches a previous it is 2 out of 4
    elif value10 == value00 or value10 == value01:
      value = value10

  if value11 != 0:
    if value == 0:
      value = value10
    elif value11==value00 or value11==value01 or value11==value10:
      value = value11

  return value



def addData ( cube, output, offset ):
    """Add the contribution of the input data to the next level at the given offset in the output cube"""

    for z in range (cube.data.shape[0]):
      for y in range (cube.data.shape[1]/2):
        for x in range (cube.data.shape[2]/2):
           
            value = getAnnValue (cube.data[z,y*2,x*2],cube.data[z,y*2,x*2+1],cube.data[z,y*2+1,x*2],cube.data[z,y*2+1,x*2+1])
            output [ z+offset[2], y+offset[1], x+offset[0] ] = value



def pngto32 ( np.ndarray[np.uint8_t,ndim=3] data ):
  """Convert the numpy array of PNG channels to 32 bit integers"""

  # I think this is yxchannel indexing 
  cdef int xrange = data.shape[1]
  cdef int yrange = data.shape[0]

  cdef np.ndarray newdata = np.zeros([yrange,xrange], dtype=np.uint32) 

  for y in range (yrange):
    for x in range(xrange):
      newdata[y,x] = (data[y,x,0] << 16) + (data[y,x,1] << 8) + data[y,x,2]

  return newdata 
       
