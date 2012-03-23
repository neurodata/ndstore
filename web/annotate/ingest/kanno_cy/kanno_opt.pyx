
import numpy as np
cimport numpy as np

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

#STYPE = np.uint8
#ctypedef np.uint8_t STYPE

def getAnnotations ( np.ndarray[DTYPE_t, ndim=2] imgdata ):

  voxels = []

  it = np.nditer ( imgdata, flags=['multi_index'], op_flags=['readonly'] )
  while not it.finished:
    if ( it[0] != 0 ):
      voxels.append ( [ it[0], it.multi_index[1], it.multi_index[0]] ) 
    it.iternext()

  return voxels

def transferAnnotations ( np.ndarray[np.uint8_t, ndim=3] input):
  """Compiled accelerator to combine RBG png values into one int"""

  cdef np.ndarray output = np.zeros([input.shape[0],input.shape[1]], dtype=DTYPE)

  cdef int y  
  cdef int x
  for x in range ( input.shape[0] ):
    for y in range ( input.shape[1] ):
      output [x,y] = (input[x,y][0] << 16) + (input[x,y][1] << 8) + input[x,y][2]

#  it = np.nditer ( input, flags=['multi_index'], op_flags=['readonly'] )
#  while not it.finished:
#    output [ it.multi_index[0], it.multi_index[1] ] = it[0]
#    it.iternext()

  return output

