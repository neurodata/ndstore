# Copyright 2015 NeuroData (http://neurodata.io)
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

import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO
from contextlib import closing
import zlib

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from django.conf import settings

import django
django.setup()

from cube import Cube
from ndproj import NDProjectsDB
from spatialdb import SpatialDB

""" Determine a histogram from an image stack """

class ImgHist():
  """ Get the histogram for an image dataset by getting individual histograms for cube aligned cutouts, then summing """

  def __init__(self, token, channel, res, bits):
    self.token = token
    self.channel = channel
    self.res = int(res)
    self.numbins = 2**int(bits)

  def getHist(self):

    with closing (NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing (SpatialDB(proj)) as db:
      ch = proj.getChannelObj(self.channel)

      # Get the source database sizes
      [[ximagesz, yimagesz, zimagesz], timerange] = proj.datasetcfg.imageSize(self.res)
      [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.res]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.res]

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = (ximagesz-1) / xcubedim + 1
      ylimit = (yimagesz-1) / ycubedim + 1
      zlimit = (zimagesz-1) / zcubedim + 1

      hist_sum = np.zeros(self.numbins, dtype=np.uint32)

      # sum the histograms
      for z in range(zlimit):
        for y in range(ylimit):
          for x in range(xlimit):

            # cutout the data for the cube
            data = db.cutout(ch, [ x*xcubedim, y*ycubedim, z*zcubedim], cubedim, self.res ).data

            # compute the histogram and store it
            (hist, bins) = np.histogram(data[data > 0], bins=self.numbins, range=(0,self.numbins))
            hist_sum = np.add( hist_sum, hist )
            print "Processed cube {} {} {}".format(x,y,z)

      return (hist_sum, bins)

class ImgHistROI():
  """ Get the histogram for a specific ROI in an image dataset by getting individual histograms for cube aligned cutouts, then summing """

  def __init__(self, token, channel, res, bits, roi):
    self.token = token
    self.channel = channel
    self.res = int(res)
    self.numbins = 2**int(bits)

    # parse roi
    self.roi_lower = roi[0]
    self.roi_upper = roi[1]

  def getHist(self):

    with closing (NDProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing (SpatialDB(proj)) as db:
      ch = proj.getChannelObj(self.channel)

      [ xcubedim, ycubedim, zcubedim ] = cubedim = proj.datasetcfg.cubedim[self.res]
      effcorner = self.roi_lower
      effdim = self.roi_upper

      # get starting and ending indices
      zstart = (effcorner[2])/zcubedim
      ystart = (effcorner[1])/ycubedim
      xstart = (effcorner[0])/xcubedim

      zend = (effdim[2])/zcubedim
      yend = (effdim[1])/ycubedim
      xend = (effdim[0])/xcubedim

      hist_sum = np.zeros(self.numbins, dtype=np.uint32)

      # sum the histogram
      # we want to iterate over indices, checking for partial cubes
      for z in range(zstart, zend + 1):
        for y in range(ystart, yend + 1):
          for x in range(xstart, xend + 1):
            # cutout the data for the cube
            cube = db.cutout(ch, [ x*xcubedim, y*ycubedim, z*zcubedim], cubedim, self.res )

            cubestart = [0, 0, 0]
            cubeend = [xcubedim, ycubedim, zcubedim]

            # check for partial cube
            if x == xstart:
              cubestart[0] = effcorner[0] - x*xcubedim
            if y == ystart:
              cubestart[1] = effcorner[1] - y*ycubedim
            if z == zstart:
              cubestart[2] = effcorner[2] - z*zcubedim

            if x == xend:
              cubeend[0] = effdim[0] - x*xcubedim
            if y == yend:
              cubeend[1] = effdim[1] - y*ycubedim
            if z == zend:
              cubeend[2] = effdim[2] - z*zcubedim

            # trim cube if necessary
            data = cube.data[cubestart[2]:cubeend[2], cubestart[1]:cubeend[1], cubestart[0]:cubeend[0]]

            # compute the histogram and store it
            (hist, bins) = np.histogram(data[data > 0], bins=self.numbins, range=(0,self.numbins))
            hist_sum = np.add( hist_sum, hist )
            print "Processed cube {} {} {}".format(x,y,z)

      return (hist_sum, bins)
