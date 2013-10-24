import numpy as np
cimport numpy as np
import zindex

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

#######################   Annotate -- list processing optimized ##########################

def annotate_cy ( np.ndarray[DTYPE_t, ndim=3] data, unsigned int annid, offset, np.ndarray[DTYPE_t, ndim=2] locations, conflictopt ):
  """Add annotation by a list of locations"""

  cdef unsigned int xoffset
  cdef unsigned int yoffset
  cdef unsigned int zoffset

  xoffset, yoffset, zoffset = offset

  exceptions = []


  # xyz coordinates get stored as zyx to be more
  #  efficient when converting to images
  for i in range (len(locations)):
    voxel = locations[i]

#    if xoffset<voxel[0] or yoffset<voxel[1] or zoffset<voxel[2]:
#      raise Exception( '{},{},{}{}'.format(xoffset, yoffset, zoffset, voxel))

    #  label unlabeled voxels
    if ( data [ voxel[2]-zoffset, voxel[1]-yoffset, voxel[0]-xoffset] == 0 ):
         data [ voxel[2]-zoffset, voxel[1]-yoffset, voxel[0]-xoffset ] = annid

    # already labelled voxels are exceptions, unless they are the same value
    elif (data [ voxel[2]-zoffset, voxel[1]-yoffset, voxel[0]-xoffset] != annid ):
      # O is for overwrite
      if conflictopt == 'O':
        data [ voxel[2]-zoffset, voxel[1]-yoffset, voxel[0]-xoffset ] = annid
      # P preserves the existing content
      elif conflictopt == 'P':
        pass
      # E creates exceptions
      elif conflictopt == 'E':
        exceptions.append ([voxel[0]-xoffset, voxel[1]-yoffset, voxel[2]-zoffset])
      else:
        print ( "Improper conflict option selected.  Option = ", conflictopt  )
        assert 0

  return exceptions


####################  shave -- remove a list of voxels from an annotation   ############################

def shave_cy ( np.ndarray[DTYPE_t, ndim=3] data, int annid, offset, np.ndarray[DTYPE_t, ndim=2] locations ):
  """Remove annotation by a list of locations"""

  cdef int xoffset
  cdef int yoffset
  cdef int zoffset

  xoffset, yoffset, zoffset = offset

  exceptions = []
  zeroed = []              # candidates for promotion

  # xyz coordinates get stored as zyx to be more
  #  efficient when converting to images
  for i in range (len(locations)):

    voxel = locations[i]
    #  if it's labeled, remove the label
    if ( data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] == annid ):
         data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0] ] = 0
         zeroed.append ( [voxel[0]-offset[0], voxel[1]-offset[1], voxel[2]-offset[2]] )

    # already labelled voxels may be in the exceptions list
    elif (data [ voxel[2]-offset[2], voxel[1]-offset[1], voxel[0]-offset[0]] != 0 ):
      exceptions.append ([voxel[0]-offset[0], voxel[1]-offset[1], voxel[2]-offset[2]])

  return exceptions, zeroed


#################  Annotation recoloring function   ##################

# 10 color categorical from colorbrewer
pcolors = ((166, 206, 227),\
(31, 120, 180),\
(178, 223, 138),\
(51, 160, 44),\
(251, 154, 153),\
(227, 26, 28),\
(253, 191, 111),\
(255, 127, 0),\
(202, 178, 214),\
(106, 61, 154),\
(255, 255, 153))

rgbcolor=[]
for pc in pcolors:
  rgbcolor.append((0xFF<<24)+(pc[0]<<16)+(pc[1]<<8)+pc[2])
#  for will temporary
#  rgbcolor.append((0xA0<<24)+(pc[0]<<16)+(pc[1]<<8)+pc[2])

def recolor_cy ( np.ndarray[np.uint32_t, ndim=2] cutout, np.ndarray[np.uint32_t, ndim=2] imagemap ):
  """Annotation recoloring function."""

  cdef int i
  cdef int j
  for j in range ( cutout.shape[0] ):
    for i in range ( cutout.shape[1] ):
      if cutout[j,i]!=0:
        imagemap[j,i] = rgbcolor[cutout[j,i]%10]


#################  Tight cutout function ##################

def assignVoxels_cy ( np.ndarray[np.uint32_t, ndim=2] voxarray, np.ndarray[np.uint32_t, ndim=3] cutout, int annoid, int xmin, int ymin, int zmin):
  """Set the voxels specified in voxarray to annoid in the cutout data"""

  cdef int a
  cdef int b
  cdef int c
  for (a,b,c) in voxarray:
    cutout[c-zmin,b-ymin,a-xmin] = annoid 


#################  Loop  for uploading voxels function ##################

def cubeLocs_cy ( np.ndarray[np.uint32_t, ndim=2] locations, cubedim ):

  cdef int i

  cubelocs = np.zeros ( [len(locations),4], dtype=np.uint32 )

  #  construct a list of the voxels in each cube using arrays
  for i in range(len(locations)):
    loc = locations[i]
    cubeno = loc[0]/cubedim[0], loc[1]/cubedim[1], loc[2]/cubedim[2]
    cubekey = zindex.XYZMorton(cubeno)
    cubelocs[i]=[cubekey,loc[0],loc[1],loc[2]]

  return cubelocs



####  RB? Maybe these need to go elsewhere?


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

def addData_cy ( cube, output, offset ):
    """Add the contribution of the input data to the next level at the given offset in the output cube"""

    for z in range (cube.data.shape[0]):
      for y in range (cube.data.shape[1]/2):
        for x in range (cube.data.shape[2]/2):
           
            value = getAnnValue (cube.data[z,y*2,x*2],cube.data[z,y*2,x*2+1],cube.data[z,y*2+1,x*2],cube.data[z,y*2+1,x*2+1])
            output [ z+offset[2], y+offset[1], x+offset[0] ] = value


def zoomData_cy ( np.ndarray[np.uint32_t, ndim=3] olddata, np.ndarray[np.uint32_t, ndim=3] newdata, int factor ):
    """Add the contribution of the input data to the next level at the given offset in the output cube"""

    cdef int z
    cdef int y
    cdef int x
    for z in range (newdata.shape[0]):
      for y in range (newdata.shape[1]):
        for x in range (newdata.shape[2]):
          newdata[z,y,x] = olddata[z,y/(2**factor),x/(2**factor)]

#######################   Annotate -- list processing optimized ##########################

def mergeCube_cy ( np.ndarray[DTYPE_t, ndim=3] data, unsigned int newid, unsigned int oldid):
    """Relabel voxels in cuve from oldid to newid"""
    cdef int z
    cdef int y
    cdef int x
    for z in range (data.shape[0]):
      for y in range (data.shape[1]):
        for x in range (data.shape[2]):
          if data[z,y,x]== oldid:
            data[z,y,x]=newid
	      




  