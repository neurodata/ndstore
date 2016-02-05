# Copyright 2014 NeuroData (http://neurodata.io)
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

import os
import ctypes as cp
import numpy as np
import numpy.ctypeslib as npct
import rgbColor

#
# Cube Locations using ctypes
#

# Load the shared C library using ctype mechanism and the directory path is always local
BASE_PATH = os.path.dirname(__file__)
ndlib = npct.load_library("ndlib", BASE_PATH+"/c_version") 
# Load the shared CPP library using ctype mechanism and the directory path is always local
#ndlib = npct.load_library("ndlib", "cpp_version") 

array_1d_uint8 = npct.ndpointer(dtype=np.uint8, ndim=1, flags='C_CONTIGUOUS')
array_2d_uint8 = npct.ndpointer(dtype=np.uint8, ndim=2, flags='C_CONTIGUOUS')
array_1d_uint16 = npct.ndpointer(dtype=np.uint16, ndim=1, flags='C_CONTIGUOUS')
array_2d_uint16 = npct.ndpointer(dtype=np.uint16, ndim=2, flags='C_CONTIGUOUS')
array_3d_uint16 = npct.ndpointer(dtype=np.uint16, ndim=3, flags='C_CONTIGUOUS')
array_1d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=1, flags='C_CONTIGUOUS')
array_2d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=2, flags='C_CONTIGUOUS')
array_3d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=3, flags='C_CONTIGUOUS')
array_1d_uint64 = npct.ndpointer(dtype=np.uint64, ndim=1, flags='C_CONTIGUOUS')
array_2d_uint64 = npct.ndpointer(dtype=np.uint64, ndim=2, flags='C_CONTIGUOUS')
array_2d_float32 = npct.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS')


# defining the parameter types of the functions in C
# FORMAT: <library_name>,<functiona_name>.argtypes = [ ctype.<argtype> , ctype.<argtype> ....]

ndlib.filterCutout.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
ndlib.filterCutoutOMP.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
ndlib.locateCube.argtypes = [ array_2d_uint64, cp.c_int, array_2d_uint32, cp.c_int, cp.POINTER(cp.c_int) ]
ndlib.annotateCube.argtypes = [ array_1d_uint32, cp.c_int, cp.POINTER(cp.c_int), cp.c_int, array_1d_uint32, array_2d_uint32, cp.c_int, cp.c_char, array_2d_uint32 ]
ndlib.XYZMorton.argtypes = [ array_1d_uint64 ]
ndlib.MortonXYZ.argtypes = [ npct.ctypes.c_int64 , array_1d_uint64 ]
ndlib.recolorCubeOMP.argtypes = [ array_2d_uint32, cp.c_int, cp.c_int, array_2d_uint32, array_1d_uint32 ]
ndlib.quicksort.argtypes = [ array_2d_uint64, cp.c_int ]
ndlib.shaveCube.argtypes = [ array_1d_uint32, cp.c_int, cp.POINTER(cp.c_int), cp.c_int, array_1d_uint32, array_2d_uint32, cp.c_int, array_2d_uint32, cp.c_int, array_2d_uint32 ]
ndlib.annotateEntityDense.argtypes = [ array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.shaveDense.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int) ]
ndlib.exceptionDense.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int) ]
ndlib.overwriteDense.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int) ]
ndlib.zoomOutData.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.zoomOutDataOMP.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.zoomInData.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.zoomInDataOMP16.argtypes = [ array_3d_uint16, array_3d_uint16, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.zoomInDataOMP32.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int ]
ndlib.mergeCube.argtypes = [ array_3d_uint32, cp.POINTER(cp.c_int), cp.c_int, cp.c_int ]
ndlib.isotropicBuild8.argtypes = [ array_2d_uint8, array_2d_uint8, array_2d_uint8, cp.POINTER(cp.c_int) ]
ndlib.isotropicBuild16.argtypes = [ array_2d_uint16, array_2d_uint16, array_2d_uint16, cp.POINTER(cp.c_int) ]
ndlib.isotropicBuild32.argtypes = [ array_2d_uint32, array_2d_uint32, array_2d_uint32, cp.POINTER(cp.c_int) ]
ndlib.isotropicBuildF32.argtypes = [ array_2d_float32, array_2d_float32, array_2d_float32, cp.POINTER(cp.c_int) ]
ndlib.addDataZSlice.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.POINTER(cp.c_int) ]
ndlib.addDataIsotropic.argtypes = [ array_3d_uint32, array_3d_uint32, cp.POINTER(cp.c_int), cp.POINTER(cp.c_int) ]
ndlib.unique.argtypes = [ array_1d_uint32, array_1d_uint32, cp.c_int ]

# setting the return type of the function in C
# FORMAT: <library_name>.<function_name>.restype = [ ctype.<argtype> ]

ndlib.filterCutout.restype = None
ndlib.filterCutoutOMP.restype = None
ndlib.locateCube.restype = None
ndlib.annotateCube.restype = cp.c_int
ndlib.XYZMorton.restype = npct.ctypes.c_uint64
ndlib.MortonXYZ.restype = None
ndlib.recolorCubeOMP.restype = None
ndlib.quicksort.restype = None
ndlib.shaveCube.restype = None
ndlib.annotateEntityDense.restype = None
ndlib.shaveDense.restype = None
ndlib.exceptionDense.restype = None
ndlib.overwriteDense.restype = None
ndlib.zoomOutData.restype = None
ndlib.zoomOutDataOMP.restype = None
ndlib.zoomInData.restype = None
ndlib.zoomInDataOMP16.restype = None
ndlib.zoomInDataOMP32.restype = None
ndlib.mergeCube.restype = None
ndlib.isotropicBuild8.restype = None
ndlib.isotropicBuild16.restype = None
ndlib.isotropicBuild32.restype = None
ndlib.isotropicBuildF32.restype = None
ndlib.addDataZSlice.restype = None
ndlib.addDataIsotropic.restype = None
ndlib.unique.restype = cp.c_int

def filter_ctype_OMP ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist using OpenMP"""
  
  # get a copy of the iterator as a 1-D array
  cutout_shape = cutout.shape
  # Temp Fix
  cutout = np.asarray(cutout, dtype=np.uint32)
  cutout = cutout.ravel()
  filterlist = np.asarray(filterlist, dtype=np.uint32)
  
  #Calling the C openmp funtion 
  ndlib.filterCutoutOMP ( cutout, cp.c_int(len(cutout)), np.sort(filterlist), cp.c_int(len(filterlist)) )
  
  return cutout.reshape( cutout_shape )
           

def filter_ctype ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist"""
                
  # get a copy of the iterator as a 1-D array
  flatcutout = cutout.flat.copy()
  
  # Calling the C naive function
  ndlib.filterCutout(flatcutout,cp.c_int(len(flatcutout)),filterlist,cp.c_int(len(filterlist)))

  return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])


def annotate_ctype ( data, annid, offset, locations, conflictopt ):
  """ Remove all annotations in a cutout that do not match the filterlist """

  # get a copy of the iterator as a 1-D array
  datashape = data.shape
  dims = [i for i in data.shape]
  data = data.ravel()

  exceptions = np.zeros ( (len(locations),3), dtype=np.uint32 )
          
  # Calling the C native function
  exceptionIndex = ndlib.annotateCube ( data, cp.c_int(len(data)), (cp.c_int * len(dims))(*dims), cp.c_int(annid), offset, locations, cp.c_int(len(locations)), cp.c_char(conflictopt), exceptions )

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
  ndlib.locateCube ( cubeLocs, cp.c_int(len(cubeLocs)), locations, cp.c_int(len(locations)), (cp.c_int * len(dims))(*dims) )
  
  return cubeLocs


def XYZMorton ( xyz ):
  """ Get morton order from XYZ coordinates """
  
  # Calling the C native function
  xyz = np.uint64( xyz )
  morton = ndlib.XYZMorton ( xyz )
  
  return morton


def MortonXYZ ( morton ):
  """ Get morton order from XYZ coordinates """
  
  # Calling the C native function
  morton = np.uint64(morton)
  cubeoff = np.zeros((3), dtype=np.uint64)
  ndlib.MortonXYZ ( morton, cubeoff )
  
  cubeoff = np.uint32(cubeoff)
  return [i for i in cubeoff]

def recolor_ctype ( cutout, imagemap ):
  """ Annotation recoloring function """
  
  xdim, ydim = cutout.shape
  if not cutout.flags['C_CONTIGUOUS']:
    cutout = np.ascontiguousarray(cutout,dtype=np.uint32)
  # Calling the c native function
  ndlib.recolorCubeOMP ( cutout, cp.c_int(xdim), cp.c_int(ydim), imagemap, np.asarray( rgbColor.rgbcolor,dtype=np.uint32) )
  return imagemap

def recolor64_ctype ( cutout, imagemap ):
  """ Annotation recoloring function """
  
  xdim, ydim = cutout.shape
  if not cutout.flags['C_CONTIGUOUS']:
    cutout = np.ascontiguousarray(cutout,dtype=np.uint32)
  # Calling the c native function
  ndlib.recolor64CubeOMP ( cutout, cp.c_int(xdim), cp.c_int(ydim), imagemap, np.asarray( rgbColor.rgbcolor,dtype=np.uint32) )
  return imagemap

def quicksort ( locs ):
  """ Sort the cube on Morton Id """

  # Calling the C native language
  ndlib.quicksort ( locs, len(locs) )
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
  ndlib.shaveCube ( data, cp.c_int(len(data)), (cp.c_int * len(dims))(*dims), cp.c_int(annid), offset, locations, cp.c_int(len(locations)), exceptions, cp.c_int(exceptionIndex), zeroed, cp.c_int(zeroedIndex) )

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
  ndlib.annotateEntityDense ( data, (cp.c_int * len(dims))(*dims), cp.c_int(entityid) )
  return ( data )


def shaveDense_ctype ( data, shavedata ):
  """ Remove the specified voxels from the annotation """

  dims = [ i for i in data.shape ]
  ndlib.shaveDense ( data, shavedata, (cp.c_int * len(dims))(*dims) )
  return ( data )


def exceptionDense_ctype ( data, annodata ):
  """ Get a dense voxel region and overwrite all the non-zero values """

  data = np.uint32(data)
  annodata = np.uint32(annodata)
  if not annodata.flags['C_CONTIGUOUS']:
    annodata = np.ascontiguousarray(annodata,np.uint32)
  dims = [ i for i in data.shape ]
  ndlib.exceptionDense ( data, annodata, (cp.c_int * len(dims))(*dims) )
  return ( data )


def overwriteDense_ctype ( data, annodata ):
  """ Get a dense voxel region and overwrite all the non-zero values """

  orginal_dtype = data.dtype
  data = np.uint32(data)
  annodata = np.uint32(annodata)
  #data = np.ascontiguousarray(data,dtype=np.uint32)
  if not annodata.flags['C_CONTIGUOUS']:
    annodata = np.ascontiguousarray(annodata,dtype=np.uint32)
  dims = [ i for i in data.shape ]
  ndlib.overwriteDense ( data, annodata, (cp.c_int * len(dims))(*dims) )
  return ( data.astype(orginal_dtype, copy=False) )


def zoomOutData_ctype ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  ndlib.zoomOutData ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )
  return ( newdata )

def zoomOutData64_ctype ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  ndlib.zoomOutData64 ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )
  return ( newdata )

def zoomOutData_ctype_OMP ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  ndlib.zoomOutDataOMP ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )
  return ( newdata )


def zoomInData_ctype ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  ndlib.zoomInData ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )
  return ( newdata )

def zoomInData_ctype_OMP ( olddata, newdata, factor ):
  """ Add the contribution of the input data to the next level at the given offset in the output cube """

  dims = [ i for i in newdata.shape ]
  if olddata.dtype == np.uint16:
    ndlib.zoomInDataOMP16 ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) ) 
  else:
    ndlib.zoomInDataOMP32 ( olddata, newdata, (cp.c_int * len(dims))(*dims), cp.c_int(factor) )
  return ( newdata )

def mergeCube_ctype ( data, newid, oldid ):
  """ Relabel voxels in cube from oldid to newid """

  dims = [ i for i in data.shape ]
  ndlib.mergeCube ( data, (cp.c_int * len(dims))(*dims), cp.c_int(newid), cp.c_int(oldid) )
  return ( data )

def isotropicBuild_ctype ( data1, data2 ):
  """ Merging Data """

  dims = [ i for i in data1.shape ]
  newdata = np.zeros(data1.shape,dtype=data1.dtype)
  if data1.dtype == np.uint32:
    ndlib.isotropicBuild32 ( data1, data2, newdata, (cp.c_int * len(dims))(*dims) )
  elif data1.dtype == np.uint8:
    ndlib.isotropicBuild8 ( data1, data2, newdata, (cp.c_int * len(dims))(*dims) )
  elif data1.dtype == np.uint16:
    ndlib.isotropicBuild16 ( data1, data2, newdata, (cp.c_int * len(dims))(*dims) )
  elif data1.dtype == np.float32:
    ndlib.isotropicBuildF32 ( data1, data2, newdata, (cp.c_int * len(dims))(*dims) )
  else:
    raise 
  return ( newdata )

def addDataToIsotropicStack_ctype ( cube, output, offset ):
  """Add the contribution of the input data to the next level at the given offset in the output cube"""

  dims = [ i for i in cube.data.shape ]
  ndlib.addDataIsotropic ( cube.data, output, (cp.c_int * len(offset))(*offset), (cp.c_int * len(dims))(*dims) )

def addDataToZSliceStack_ctype ( cube, output, offset ):
  """Add the contribution of the input data to the next level at the given offset in the output cube"""

  dims = [ i for i in cube.data.shape ]
  ndlib.addDataZSlice ( cube.data, output, (cp.c_int * len(offset))(*offset), (cp.c_int * len(dims))(*dims) )

def unique ( data ):
  """Return the unqiue elements in the array"""

  data = data.ravel()
  unique_array = np.zeros(len(data), dtype=data.dtype)
  unique_length = ndlib.unique ( data, unique_array, cp.c_int(len(data)) )

  return unique_array[:unique_length]

#def annoidIntersect_ctype_OMP(cutout, annoid_list):
  #"""Remove all annotations in a cutout that do not match the filterlist using OpenMP"""
  
  ## get a copy of the iterator as a 1-D array
  #cutout = cutout.ravel()
  #annoid_list = np.asarray(annoid_list, dtype=np.uint32)
  
  ## Calling the C openmp funtion 
  #ndlib.annoidIntersectOMP(cutout, cp.c_int(len(cutout)), np.sort(annoid_list), cp.c_int(len(annoid_list)))
  
  #return cutout.reshape( cutout_shape )
