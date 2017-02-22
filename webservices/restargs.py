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

#
#  Check the formatting of RESTful arguments.
#  Shared by cutout and annotation services.
#

import re
import numpy as np


#
# General rest argument processing exception
#
class RESTArgsError(Exception):
  """Illegal arguments"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class BrainRestArgs:

  # Accessors to get corner and dimensions
  def getCorner (self):
    return self.corner

  def getDim (self):
   return self.dim
   
  def getResolution (self):
   return self.resolution

  def getFilter ( self ):
    return self.filterlist

  def getWindowRange ( self ):
    return self.window
  
  def getTimeRange ( self ):
    return self.time
  
  def getZScaling ( self ):
    return self.zscaling


  def cutoutArgs ( self, imageargs, datasetcfg, channels=None ):
    """Process REST arguments for an cutout plane request"""

    try:
      # argument of format /resolution/x1,x2/y1,y2/z1,z2/rest(can include t1,t2)/
      #m = re.match("([0-9]+)/([0-9]+),([0-9]+)/([0-9]+),([0-9]+)/([0-9]+),([0-9]+)([/]*[\w+]*[/]*[\d,+]*[/]*)$", imageargs)
      m = re.match("([0-9]+)/([0-9]+),([0-9]+)/([0-9]+),([0-9]+)/([0-9]+),([0-9]+)(.*)?$", imageargs)
      [self.resolution, x1, x2, y1, y2, z1, z2] = [int(i) for i in m.groups()[:-1]]
      rest = m.groups()[-1]

    except Exception as e:
      raise RESTArgsError("Incorrect cutout arguments {}. {}".format(imageargs, e))

    if self.resolution not in datasetcfg.resolutions:
      raise RESTArgsError("Illegal scaling level {}".format(imageargs))

    # Convert cutout into 0 base in all dimensions
    (xoffset,yoffset,zoffset) = [np.uint32(i) for i in datasetcfg.get_offset(self.resolution)]

    (x1, x2) = (x1-xoffset, x2-xoffset)
    (y1, y2) = (y1-yoffset, y2-yoffset)
    (z1, z2) = (z1-zoffset, z2-zoffset)
    self.corner = [x1, y1, z1]
    self.dim = [x2-x1, y2-y1, z2-z1]

    # time arguments
    self.time = None
    result = re.match("/(\d+),(\d+)/", rest)
    if result is not None:
      self.time = [int(i) for i in result.groups()]

    # Check arguments for legal values
    try:
      if not ( datasetcfg.checkCube(self.resolution, self.corner, self.dim) ):
        raise RESTArgsError ( "Illegal range. Image size: {} at offset {}".format(str(datasetcfg.dataset_dim(self.resolution)),str(datasetcfg.get_offset(self.resolution))))
    except Exception as e:
      raise RESTArgsError ( "Illegal arguments to cutout. Check cube failed {}".format(str(e)))

    # window argument
    result = re.match ("/window/([\d\.]+),([\d\.]+)/", rest)
    if result != None:
      self.window = [str(i) for i in result.groups()]
    else:
      self.window = None
    
    # list of identifiers to keep
    result = re.match ("/filter/([\d/,]+)/", rest)
    if result != None:
      self.filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    else:
      self.filterlist = None
    
    # See if it is an isotropic cutout request
    self.zscaling = None
    result = re.match ("/iso/",rest)
    if result is not None:
      self.zscaling = 'isotropic'
     
    # See if it is an integral cutout request
    result = re.match ("/neariso/",rest)
    if result is not None:
      self.zscaling = 'nearisotropic'


def voxel ( imageargs, datasetcfg ):
  """Process REST arguments for a single point"""
  
  try:
    # argument of format /resolution/x/y1,y2/z1,z2/
    m = re.match("(\w+)/(\w+)/(\w+)/(\w+)/", imageargs)
    [res, x, y, z]  = [int(i) for i in m.groups()]
  except:
    raise RESTArgsError ("Bad arguments to voxel {}".format(imageargs))

  # Check arguments for legal values
  if not ( datasetcfg.checkCube ( res, [x,y,z], [1,1,1] )):
    raise RESTArgsError( "Illegal range. Image size: {} at offset {}".format(datasetcfg.dataset_dim(res),datasetcfg.get_offset(res)) )

  return (res, [ x,y,z ])


#
#  Process cutout arguments
#
def conflictOption  ( imageargs ):
  """Parse the conflict resolution string"""

  restargs = imageargs.split('/')
  if len (restargs) > 0:
    if restargs[0] == 'preserve':
      return b'P'
    elif restargs[0] == 'except':
      return b'E'
    else:
      return b'O'

                                                                                 
def annotationId ( webargs, datasetcfg ):
  """Process REST arguments for a single"""

  rangeargs = webargs.split('/')
  # PYTODO: check validity of annotation id                                      
  return int(rangeargs[0])
