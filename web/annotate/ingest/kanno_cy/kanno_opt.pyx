
import numpy as np
cimport numpy as np

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

def getAnnotations ( np.ndarray[DTYPE_t, ndim=2] imgdata ):

  voxels = []

  it = np.nditer ( imgdata, flags=['multi_index'], op_flags=['readonly'] )
  while not it.finished:
    if ( it[0] != 0 ):
      voxels.append ( [ it[0], it.multi_index[1], it.multi_index[0]] ) 
    it.iternext()

  return voxels
