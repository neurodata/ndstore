
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


