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
# Filter Cutout using ctypes
# Has 2 implentations of filter function
# 1 - Naive Implementation 
# 2 - OpenMP Implementation
#

# Getting the filter directory path
filterdirpath = os.path.join(OCP.ocppaths.OCP_OCPCA_PATH,"filterlib")
# Load the shared C library using numpy mechanism
filterlib = npct.load_library("filterCutout",filterdirpath) 
filterlibOMP = npct.load_library("filterCutoutOMP",filterdirpath)

array_1d_uint32 = npct.ndpointer(dtype=np.uint32, ndim=1, flags='CONTIGUOUS')

# defining the parameter types of the functions in C
# FORMAT: <library_name>,<functiona_name>.argtypes = [ ctype.<argtype> , ctype.<arg    type> ....]
filterlib.filterCutout.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]
filterlibOMP.filterCutoutOMP.argtypes = [array_1d_uint32, cp.c_int, array_1d_uint32, cp.c_int]

# setting the return type of the function in C
# FORMAT: <library_name>.<function_name>.restype = [ ctype.<argtype> ]
filterlib.filterCutout.restype = None
filterlibOMP.filterCutoutOMP.restype = None

# Uses OpenMP for filtercutout
def filterCutoutCtypeOMP ( cutout, filterlist ):
		"""Remove all annotations in a cutout that do not match the filterlist using OpenMP"""
		# get a copy of the iterator as a 1-D array
		flatcutout = cutout.flat.copy()
		#Calling the C openmp funtion 
		filterlibOMP.filterCutoutOMP(flatcutout,cp.c_int(len(flatcutout)),filterlist,cp.c_int(len(filterlist)))
		return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])

# Uses naive implementation of C for filtercutout
def filterCutoutCtype ( cutout, filterlist ):
		"""Remove all annotations in a cutout that do not match the filterlist"""
		# get a copy of the iterator as a 1-D array
		flatcutout = cutout.flat.copy()
		# Calling the C naive function
		filterlib.filterCutout(flatcutout,cp.c_int(len(flatcutout)),filterlist,cp.c_int(len(filterlist)))
		return flatcutout.reshape(cutout.shape[0],cutout.shape[1],cutout.shape[2])
