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
