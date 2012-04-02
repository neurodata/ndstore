
import numpy as np
cimport numpy as np

cdef inline int merge_func ( np.uint8_t a, np.uint8_t b, np.uint8_t c ): 
  return (int(a) << 16) + (int(b) << 8) + c


#cdef void pngMerge ( int offset, np.ndarray[np.uint32_t, ndim=3] newdata, np.ndarray[np.uint8_t, ndim=3] imgdata ):
def pngMerge ( int offset, np.ndarray[np.uint32_t, ndim=3] newdata, np.ndarray[np.uint8_t, ndim=3] imgdata ):

  cdef int x
  cdef int y

  for y in range ( 8192 ):
    for x in range ( 8192 ): 
      newdata[offset,y,x] = merge_func ( imgdata[y,x,2], imgdata[y,x,1], imgdata[y,x,0] )
