# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

import argparse
import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO
from contextlib import closing
import zlib

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

from cube import Cube
import ocpcarest
import ocplib
import ocpcaproj
import ocpcadb

""" Determine the median, stddev, min, max, and percentile values given a 16-bit image stack """


class ImgHist():
  """ Get the histogram for an image dataset by getting individual histograms for cube aligned cutouts, then summing """  
  
  def __init__(self, token, channel, res):
    self.token = token
    self.channel = channel
    self.res = int(res)
  
  def getHist(self):

    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)
    
    with closing (ocpcadb.OCPCADB(proj)) as db:
      ch = proj.getChannelObj(self.channel)

      # Get the source database sizes
      [[ximagesz, yimagesz, zimagesz], timerange] = proj.datasetcfg.imageSize(self.res)
      [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.res]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.res]

      # Set the limits for iteration on the number of cubes in each dimension
      xlimit = (ximagesz-1) / xcubedim + 1
      ylimit = (yimagesz-1) / ycubedim + 1
      zlimit = (zimagesz-1) / zcubedim + 1

      numbins = 2**16; 
      hist = []
      bins = np.zeros(numbins+1)  
      count = 0
      
      # sum the histograms 
      for z in range(zlimit):
        for y in range(ylimit):
          for x in range(xlimit):

            # cutout the data for the cube 
            data = db.cutout(ch, [ x*xcubedim, y*ycubedim, z*zcubedim], cubedim, self.res ).data
            
            # compute the histogram and store it 
            hist.append(np.histogram(data[data > 0], bins=numbins, range=(0,2**16)))
            print "Processed cube {} {} {}".format(x,y,z)
        
      # sum the individual histograms
      hist_sum = np.zeros(numbins)
      bins = hist[0][1] # all bins should be the same 
      for i in range(len(hist)):
        hist_sum += hist[i][0]

      
      return (hist_sum, bins)
      
     
  def mean(self, histogram, bins):
    """ Given a histogram and the bin widths, calculate the mean for the histogram
        and return it """
    mean_upper = 0
    mean_lower = 0
    for i, binval in enumerate(histogram):
      mean_upper += binval*( (bins[i+1] + bins[i]) / 2 )
      mean_lower += binval 

    mean = mean_upper / mean_lower
    return mean


  def stddev(self, histogram, bins, mean):
    """ Compute the standard deviation of the histogram """
    std_upper = 0
    std_lower = 0
    for i, binval in enumerate(histogram):
      std_upper += binval * ( ( ( (bins[i+1] + bins[i])/2 ) - mean )**2 )
      std_lower += binval

    stddev = np.sqrt(std_upper / std_lower)
    return stddev 

  def percentile(self, histogram, bins, percent):
    """ Calculate the <<percent>> percentile of the histogram """
    
    # normalize the histogram
    hist_norm = np.zeros(histogram.shape)
    
    hist_sum = 0
    for binval in histogram:
      hist_sum += binval
    
    for i, binval in enumerate(histogram):
      hist_norm[i] = histogram[i] / hist_sum

    # compute the percentile using the normalized histogram
    bin_sum = 0
    i = 0
    pfloat = percent * 0.01 
    while bin_sum < pfloat and i < hist_norm.shape[0] + 1:
      bin_sum += hist_norm[i]
      i += 1 

    return bins[i+1] 

  def min(self, histogram, bins):
    for i, binval in enumerate(histogram):
      if binval > 0:
        return bins[i] 

  def max(self, histogram, bins):
    max = 0
    for i, binval in enumerate(histogram):
      if binval > 0:
        max = bins[i] 

    return max 

def main():

  parser = argparse.ArgumentParser(description='Get image statistics for a 16 bit image project')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('channel', action="store", help='Channel for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Resolution for the histogram')
  parser.add_argument('--percentiles', nargs='*', type=float, help='Calculate the following percentiles (expressed as percents -- e.g., for the 99th percentile enter 99)') 

  result = parser.parse_args()

  ih = ImgHist(result.token, result.channel, result.resolution) 
  (histogram, bins) = ih.getHist()
  mean = ih.mean(histogram, bins)
  stddev = ih.stddev(histogram, bins, mean)
  minval = ih.min(histogram, bins)
  maxval = ih.max(histogram, bins)
  print "mean: {}".format(mean)
  print "stddev: {}".format(stddev)
  print "min: {}".format(minval) 
  print "max: {}".format(maxval) 
  for percentile in result.percentiles:
    perc = ih.percentile(histogram, bins, percentile)
    print "{}th percentile: {}".format( percentile, perc )
  
if __name__ == "__main__":
  main()

