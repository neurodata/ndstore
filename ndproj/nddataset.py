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

import math
from operator import add, sub, mul, div, mod

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from ndtype import *
from nduser.models import Dataset

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class NDDataset:
  """Configuration for a dataset"""

  def __init__ ( self, dataset_name ):
    """Construct a db configuration from the dataset parameters""" 
    
    try:
      self.ds = Dataset.objects.get(dataset_name = dataset_name)
    except ObjectDoesNotExist, e:
      logger.error("Dataset {} does not exist. {}".format(dataset_name, e))
      raise NDWSError("Dataset {} does not exist".format(dataset_name))

    self.resolutions = []
    self.cubedim = {}
    self.supercubedim = {}
    self.imagesz = {}
    self.offset = {}
    self.voxelres = {}
    self.scale = {}
    self.scalingoption = self.ds.scalingoption
    self.scalinglevels = self.ds.scalinglevels
    self.timerange = (self.ds.starttime, self.ds.endtime)
    # nearisotropic service for Stephan
    self.nearisoscaledown = {}
    self.neariso_voxelres = {}
    self.neariso_imagesz = {}
    self.neariso_offset = {}

    for i in range (self.ds.scalinglevels+1):
      """Populate the dictionaries"""

      # add this level to the resolutions
      self.resolutions.append( i )

      # set the image size
      #  the scaled down image rounded up to the nearest cube
      xpixels = ((self.ds.ximagesize-1)/2**i)+1
      ypixels = ((self.ds.yimagesize-1)/2**i)+1
      if self.ds.scalingoption == ZSLICES:
        zpixels = self.ds.zimagesize
      else:
        zpixels = ((self.ds.zimagesize-1)/2**i)+1
      self.imagesz[i] = [ xpixels, ypixels, zpixels ]

      # set the offset
      xoffseti = 0 if self.ds.xoffset==0 else ((self.ds.xoffset)/2**i)
      yoffseti = 0 if self.ds.yoffset==0 else ((self.ds.yoffset)/2**i)
      if self.ds.zoffset == 0:
        zoffseti = 0
      else:
        if self.ds.scalingoption == ZSLICES:
          zoffseti = self.ds.zoffset
        else:
         zoffseti = ((self.ds.zoffset)/2**i)

      self.offset[i] = [ xoffseti, yoffseti, zoffseti ]

      # set the voxelresolution
      xvoxelresi = self.ds.xvoxelres*float(2**i)
      yvoxelresi = self.ds.yvoxelres*float(2**i)
      zvoxelresi = self.ds.zvoxelres if self.ds.scalingoption == ZSLICES else self.ds.zvoxelres*float(2**i)

      self.voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi ]
      self.scale[i] = { 'xy':xvoxelresi/yvoxelresi , 'yz':zvoxelresi/xvoxelresi, 'xz':zvoxelresi/yvoxelresi }
      
      # choose the cubedim as a function of the zscale
      #self.cubedim[i] = [128, 128, 16]
      # this may need to be changed.  
      if self.ds.scalingoption == ZSLICES:
        #self.cubedim[i] = [512, 512, 16]
        self.cubedim[i] = [128, 128, 16]
        if float(self.ds.zvoxelres/self.ds.xvoxelres)/(2**i) >  0.5:
          self.cubedim[i] = [128, 128, 16]
        else: 
          self.cubedim[i] = [64, 64, 64]

        # Make an exception for bock11 data -- just an inconsistency in original ingest
        if self.ds.ximagesize == 135424 and i == 5:
          self.cubedim[i] = [128, 128, 16]
      else:
        # RB what should we use as a cubedim?
        self.cubedim[i] = [512, 512, 16]
      
      self.supercubedim[i] = map(mul, self.cubedim[i], SUPERCUBESIZE)

      if self.scale[i]['xz'] < 1.0:
        scalepixels = 1/self.scale[i]['xz']
        if ((math.ceil(scalepixels)-scalepixels)/scalepixels) <= ((scalepixels-math.floor(scalepixels))/scalepixels):
          self.nearisoscaledown[i] = int(math.ceil(scalepixels))
        else:
          self.nearisoscaledown[i] = int(math.floor(scalepixels))
      else:
        self.nearisoscaledown[i] = int(1)
      
      self.neariso_imagesz[i] = [ xpixels, ypixels, zpixels/self.nearisoscaledown[i] ]
      self.neariso_voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi*self.nearisoscaledown[i] ]
      self.neariso_offset[i] = [ float(xoffseti), float(yoffseti), float(zoffseti)/self.nearisoscaledown[i] ]


  # Accessors
  def getDatasetName(self):
    return self.ds.dataset_name
  
  def getResolutions(self):
    return self.resolutions
  
  def getPublic(self):
    return self.ds.public
  
  def getImageSize(self):
    return self.imagesz
  
  def getOffset(self):
    return self.offset
  
  def getScale(self):
    return self.scale
  
  def getVoxelRes(self):
    return self.voxelres
  
  def getCubeDims(self):
    return self.cubedim
  
  def getSuperCubeDims(self):
    return self.supercubedim
  
  def getSuperCubeSize(self):
    return SUPERCUBESIZE
  
  def getTimeRange(self):
    return self.timerange
  
  def getDatasetDescription ( self ):
    return self.ds.dataset_description

  def checkCube (self, resolution, corner, dim, timeargs=[0,0]):
    """Return true if the specified range of values is inside the cube"""

    [xstart, ystart, zstart ] = corner
    [tstart, tend] = timeargs

    [xend, yend, zend] = map(add, corner, dim) 

    if ( ( xstart >= 0 ) and ( xstart < xend) and ( xend <= self.imagesz[resolution][0]) and\
        ( ystart >= 0 ) and ( ystart < yend) and ( yend <= self.imagesz[resolution][1]) and\
        ( zstart >= 0 ) and ( zstart < zend) and ( zend <= self.imagesz[resolution][2]) and\
        ( tstart >= self.timerange[0]) and ((tstart < tend) or tstart==0 and tend==0) and (tend <= (self.timerange[1]+1))):
      return True
    else:
      return False

  def imageSize ( self, resolution ):
    """Return the image size"""
    return  [ self.imagesz [resolution], self.timerange ]
