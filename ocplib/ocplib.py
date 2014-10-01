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

#
# Cube Locations using ctypes
#

# Getting the directory path
#ocpdlibpath = os.path.join(OCP.ocppaths.OCP_OCPCA_PATH,"../ocplib")
# Load the shared C library using ctype mechanism
ocplib = npct.load_library("ocplib", OCP_OCPLIB_PATH) 

array_1d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=1, flags='CONTIGUOUS')
array_2d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=2, flags='CONTIGUOUS')


# defining the parameter types of the functions in C
# FORMAT: <library_name>,<functiona_name>.argtypes = [ ctype.<argtype> , ctype.<argtype> ....]

filterlib.filterCutout.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
filterlibOMP.filterCutoutOMP.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
locatelib.locateCube.argtypes = [ array_2d_uint32, cp.c_int, array_2d_uint32, cp.c_int, cp.POINTER(cp.c_int) ]
annotatelib.annotateCube.argtypes = [ array_1d_uint32, cp.c_int, cp.POINTER(cp.c_int), cp.c_int, cp.POINTER(cp.c_int), array_1d_uint32, cp.c_int, cp.c_char ]


# setting the return type of the function in C
# FORMAT: <library_name>.<function_name>.restype = [ ctype.<argtype> ]

filterlib.filterCutout.restype = None
filterlibOMP.filterCutoutOMP.restype = None
locatelib.locateCube.restype = None
annotatelib.annotateCube.restype = None

# Uses OpenMP for filtercutout
def filterCutoutCtypeOMP ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist using OpenMP"""
  
  # get a copy of the iterator as a 1-D array
  flatcutout = cutout.flat.copy()
  
  #Calling the C openmp funtion 
  filterlibOMP.filterCutoutOMP(flatcutout,cp.c_int(len(flatcutout)),filterlist.sort(),cp.c_int(len(filterlist)))
  
  return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])
           

# Uses naive implementation of C for filtercutout
def filterCutoutCtype ( cutout, filterlist ):
  """Remove all annotations in a cutout that do not match the filterlist"""
                
  # get a copy of the iterator as a 1-D array
  flatcutout = cutout.flat.copy()
  
  # Calling the C naive function
  filterlib.filterCutout(flatcutout,cp.c_int(len(flatcutout)),filterlist,cp.c_int(len(filterlist)))

  return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])


# Uses naive implementation of C for annotate
def annotateCtype ( data, annid, offset, locations, conflictopt ):
  """ Remove all annotations in a cutout that do not match the filterlist """

  # get a copy of the iterator as a 1-D array
  dims = [i for i in data.shape]
  datacopy = data.flat.copy()
          
  # Calling the C native function
  annotatelib.annotateCube ( datacopy, cp.c_int(len(datacopy)), (cp.c_int * len(dims))(*dims), cp.c_int(annid), (cp.c_int * len(offset))(*offset), locations.flatten(), cp.c_int(len(locations.flatten())), cp.c_char(conflictopt) )

  return datacopy.reshape( data.shape )


# Uses naive implementation of C for locating Cube
def locateCtype ( locations, dims ):
  """ Remove all annotations in a cutout that do not match the filterlist """
  
  # get a copy of the iterator as a 1-D array
  cubeLocs = np.zeros ( [len(locations),4], dtype=np.uint32 )
  
  # Calling the C native function
  locatelib.locateCube ( cubeLocs, cp.c_int(len(cubeLocs)), locations, cp.c_int(len(locations)), (cp.c_int * len(dims))(*dims) )
  
  return cubeLocs.reshape( (len(locations),4) )

