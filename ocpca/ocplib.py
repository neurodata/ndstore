# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes as cp
import numpy as np
import numpy.ctypeslib as npct
import os
import OCP.ocppaths
import rgbColor

#
# Cube Locations using ctypes
#

# Getting the directory path
#ocpdlibpath = os.path.join(OCP.ocppaths.OCP_OCPCA_PATH,"../ocplib")
# Load the shared C library using ctype mechanism
ocplib = npct.load_library("ocplib", OCP.ocppaths.OCP_OCPLIB_PATH) 

array_1d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=1, flags='CONTIGUOUS')
array_2d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=2, flags='CONTIGUOUS')
array_1d_uint64 = npct.ndpointer(dtype=np.uint64, ndim=1, flags='CONTIGUOUS')
array_2d_uint64 = npct.ndpointer(dtype=np.uint64, ndim=2, flags='CONTIGUOUS')

# defining the parameter types of the functions in C
# FORMAT: <library_name>,<functiona_name>.argtypes = [ ctype.<argtype> , ctype.<argtype> ....]

ocplib.filterCutout.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
ocplib.filterCutoutOMP.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
ocplib.locateCube.argtypes = [ array_2d_uint64, cp.c_int, array_2d_uint32, cp.c_int, cp.POINTER(cp.c_int) ]
ocplib.annotateCube.argtypes = [ array_1d_uint32, cp.c_int, cp.POINTER(cp.c_int), cp.c_int, array_1d_uint32, array_2d_uint32, cp.c_int, cp.c_char, array_2d_uint32 ]
ocplib.XYZMorton.argtypes = [ array_1d_uint64 ]
ocplib.MortonXYZ.argtypes = [ npct.ctypes.c_int64 , array_1d_uint64 ]
ocplib.recolorCube.argtypes = [ array_1d_uint32, cp.c_int, cp.c_int, array_1d_uint32, array_1d_uint32 ]
ocplib.quicksort.argtypes = [ array_2d_uint64, cp.c_int ]
ocplib.shaveCube.argtypes = [ array_1d_uint32, cp.c_int, cp.POINTER(cp.c_int), cp.c_int, array_1d_uint32, array_2d_uint32, cp.c_int, array_2d_uint32, cp.c_int, array_2d_uint32 ]
ocplib.annotateEntityDense.argtypes = [ array_1d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ocplib.shaveDense.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int) ]
ocplib.exceptionDense.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int) ]
ocplib.overwriteDense.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int) ]
ocplib.zoomOutData.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ocplib.zoomOutDataOMP.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ocplib.zoomInData.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ocplib.zoomInDataOMP.argtypes = [ array_1d_uint32, array_1d_uint32, cp.POINTER(cp.c_int), cp.c_int ]


# setting the return type of the function in C
# FORMAT: <library_name>.<function_name>.restype = [ ctype.<argtype> ]

ocplib.filterCutout.restype = None
ocplib.filterCutoutOMP.restype = None
ocplib.locateCube.restype = None
ocplib.annotateCube.restype = cp.c_int
ocplib.XYZMorton.restype = npct.ctypes.c_uint64
ocplib.MortonXYZ.restype = None
ocplib.recolorCube.restype = None
ocplib.quicksort.restype = None
ocplib.shaveCube.restype = None
ocplib.annotateEntityDense.restype = None
ocplib.shaveDense.restype = None
ocplib.exceptionDense.restype = None
ocplib.overwriteDense.restype = None
ocplib.zoomOutData.restype = None
ocplib.zoomOutDataOMP.restype = None
ocplib.zoomInData.restype = None
ocplib.zoomInDataOMP.restype = None


def filter_ctype_OMP ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist using OpenMP"""
  
  # get a copy of the iterator as a 1-D array
  cutout_shape = cutout.shape
  cutout = cutout.ravel()
  filterlist = np.asarray(filterlist, dtype=np.uint32)
  
  #Calling the C openmp funtion 
  ocplib.filterCutoutOMP ( cutout, cp.c_int(len(cutout)), np.sort(filterlist), cp.c_int(len(filterlist)) )
  
  return cutout.reshape( cutout_shape )
           

def filter_ctype ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist"""
                
  # get a copy of the iterator as a 1-D array
  flatcutout = cutout.flat.copy()
  
  # Calling the C naive function
  ocplib.filterCutout(flatcutout,cp.c_int(len(flatcutout)),filterlist,cp.c_int(len(filterlist)))

  return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])


def annotate_ctype ( data, annid, offset, locations, conflictopt ):
  """ Remove all annotations in a cutout that do not match the filterlist """

  # get a copy of the iterator as a 1-D array
  datashape = data.shape
  dims = [i for i in data.shape]
  data = data.ravel()

  exceptions = np.zeros ( (len(locations),3), dtype=np.uint32 )
          
  # Calling the C native function
  exceptionIndex = ocplib.annotateCube ( data, cp.c_int(len(data)), (cp.c_int * len(dims))(*dims), cp.c_int(annid), offset, locations, cp.c_int(len(locations)), cp.c_char(conflictopt), exceptions )

  if exceptionIndex > 0:
    exceptions = exceptions[:(exceptionIndex+1)]
  else:
    exceptions = np.zeros ( (0), dtype=np.uint32 )

  return ( data.reshape(datashape) , exceptions )


def locate_ctype ( locations, dims ):
  """ Remove all annotations in a cutout that do not match the filterlist """
  
  # get a copy of the iterator as a 1-D array
  cubeLocs = np.zeros ( [len(locations),4], dtype=np.uint64 )
  
  # Calling the C native function
  ocplib.locateCube ( cubeLocs, cp.c_int(len(cubeLocs)), locations, cp.c_int(len(locations)), (cp.c_int * len(dims))(*dims) )
  
  return cubeLocs


def XYZMorton ( xyz ):
  """ Get morton order from XYZ coordinates """
  
  # Calling the C native function
  xyz = np.uint64( xyz )
  morton = ocplib.XYZMorton ( xyz )
  
  return morton


def MortonXYZ ( morton ):
  """ Get morton order from XYZ coordinates """
  
  # Calling the C native function
  morton = np.uint64(morton)
  cubeoff = np.zeros((3), dtype=np.uint64)
  ocplib.MortonXYZ ( morton, cubeoff )
  
  cubeoff = np.uint32(cubeoff)
  return [i for i in cubeoff]

def recolor_ctype ( cutout, imagemap ):
  """ Annotation recoloring function """
  
  xdim, ydim = cutout.shape
  imagemap = imagemap.ravel()

  # Calling the c native function
  ocplib.recolorCube ( cutout.flatten(), cp.c_int(xdim), cp.c_int(ydim), imagemap, np.asarray( rgbColor.rgbcolor,dtype=np.uint32) )

  return imagemap.reshape( (xdim,ydim) )

def quicksort ( locs ):
  """ Sort the cube on Morton Id """

  # Calling the C native language
  ocplib.quicksort ( locs, len(locs) )

  return locs

def shave_ctype ( data, annid, offset, locations ):
  """ Remove annotations by a list of locations """

  # get a copy of the iterator as a 1-D array
  datashape = data.shape
  dims = [i for i in data.shape]
  data = data.ravel()

  exceptions = np.zeros ( (len(locations),3), dtype=np.uint32 )
  zeroed = np.zeros ( (len(locations),3), dtype=np.uint32 )

  exceptionIndex = -1
  zeroedIndex = -1
          
  # Calling the C native function
  ocplib.shaveCube ( data, cp.c_int(len(data)), (cp.c_int * len(dims))(*dims), cp.c_int(annid), offset, locations, cp.c_int(len(locations)), exceptions, cp.c_int(exceptionIndex), zeroed, cp.c_int(zeroedIndex) )

  if exceptionIndex > 0:
    exceptions = exceptions[:(exceptionIndex+1)]
  else:
    exceptions = np.zeros ( (0), dtype=np.uint32 )

  if zeroedIndex > 0:
    zeroed = zeroed[:(zeroedIndex+1)]
  else:
    zeroed = np.zeros ( (0), dtype=np.uint32 )
  
  return ( data.reshape(datashape) , exceptions, zeroed )


def annotateEntityDense_ctype ( data, entityid ):
  """ Relabel all non zero pixels to annotation id """

  dims = [ i for i in data.shape ]
  data = data.ravel()

  ocplib.annotateEntityDense ( data, (cp.c_int * len(dims))(*dims), cp.c_int(entityid) )

  return ( data.reshape(dims) )


def shaveDense_ctype ( data, shavedata ):
  """ Remove the specified voxels from the annotation """

  dims = [ i for i in data.shape ]
  data = data.ravel()
  shavedata = shavedata.ravel()

  ocplib.shaveDense ( data, shavedata, (cp.c_int * len(dims))(*dims) )

  return ( data.reshape(dims) )


def exceptionDense_ctype ( data, annodata ):
  """ Get a dense voxel region and overwrite all the non-zero values """

  data = np.uint32(data)
  annodata = np.uint32(annodata)
  dims = [ i for i in data.shape ]
  data = data.ravel()
  annodata = annodata.ravel()

  ocplib.exceptionDense ( data, annodata, (cp.c_int * len(dims))(*dims) )

  return ( data.reshape(dims) )


def overwriteDense_ctype ( data, annodata ):
  """ Get a dense voxel region and overwrite all the non-zero values """

  data = np.uint32(data)
  annodata = np.uint32(annodata)
  dims = [ i for i in data.shape ]
  data = data.ravel()
  annodata = annodata.ravel()

  ocplib.overwriteDense ( data, annodata, (cp.c_int * len(dims))(*dims) )

  return ( data.reshape(dims) )


def zoomOutData_ctype ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  olddata = olddata.ravel()
  newdata = newdata.ravel()

  ocplib.zoomOutData ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )

  return ( newdata.reshape(dims) )


def zoomOutData_ctype_OMP ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  olddata = olddata.ravel()
  newdata = newdata.ravel()

  ocplib.zoomOutDataOMP ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )

  return ( newdata.reshape(dims) )


def zoomInData_ctype ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  olddata = olddata.ravel()
  newdata = newdata.ravel()

  ocplib.zoomInData ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )

  return ( newdata.reshape(dims) )


def zoomInData_ctype_OMP ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  olddata = olddata.ravel()
  newdata = newdata.ravel()

  ocplib.zoomInDataOMP ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )

  return ( newdata.reshape(dims) )
