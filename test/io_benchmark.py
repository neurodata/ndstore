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

import os
import sys
import random
import argparse
import numpy as np
import tempfile
import h5py
import urllib2
import zlib
import cStringIO
import blosc
import time
import json
from operator import add, sub, mul
from functools import reduce

sys.path += [os.path.abspath('../django/')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ocpblaze.settings'

from ndlib import MortonXYZ

def getURL(url):
  """Get data"""

  try:
    # Build a post request
    req = urllib2.Request(url)
    start = time.time() 
    response = urllib2.urlopen(req)
    print time.time()-start
    return response
  except urllib2.HTTPError,e:
    print "Error"
    return e

class BenchmarkTest:

  def __init__(self, host, token, channel, resolution):
    """Init"""

    self.host = host
    self.token = token
    self.channels = [channel]
    self.resolution = resolution
    self.getProjInfo()

  def readTest(self, start_value=[0,0,0], number_iteration=13):
    """Run the Benchmark."""

    min_values = [xmin,ymin,zmin] = map(add, self.offset, start_value)
    max_values = map(add, min_values, self.dim)
    range_args = [None]*(len(min_values)+len(max_values))
    
    for i in range(0, number_iteration, 1):
      range_args[::2] = min_values
      range_args[1::2] = max_values
      # print "Size", reduce(mul, map(sub, max_values, min_values), 1)*2.0/(1024*1024)
      self.getBlosc(range_args)
      # min_values = max_values
      # max_values = map(add, map(sub, min_values, temp_values), min_values)
      min_values[2] = max_values[2]
      max_values[2] = min_values[2] + self.dim[2] 
      max_values[(i+1)%2] = start_value[(i+1)%2] + (max_values[(i+1)%2]-min_values[(i+1)%2])*2

  def getProjInfo(self):
    """Get the project info"""

    # Build the url
    url = 'http://{}/sd/{}/info/'.format(self.host, self.token)
    f = getURL(url)
    info = json.loads(f.read())
    self.dim = info['dataset']['cube_dimension'][self.resolution]
    self.imagesize = info['dataset']['imagesize'][self.resolution]
    self.offset = info['dataset']['offset'][self.resolution]

  def getBlosc(self, range_args):
    """Post data using the blosc interface"""

    # Build the url
    url = 'http://{}/sd/{}/{}/blosc/{}/{},{}/{},{}/{},{}/'.format(self.host, self.token, ','.join(self.channels), self.resolution, *range_args)
    # print url
    getURL(url)


def main():
  """Take in the arguments"""

  parser = argparse.ArgumentParser(description='Run the Benchmark script')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Token')
  parser.add_argument('channel', action="store", help='Channel')
  parser.add_argument('resolution', action="store", help='Resolution')
  parser.add_argument('--offset', nargs=3, type=int, metavar=('x','y','z'), default=[0,0,0], help='Start Offset')
  result = parser.parse_args()
 
  bt = BenchmarkTest(result.host, result.token, result.channel, result.resolution)
  bt.readTest(start_value=result.offset)

if __name__ == '__main__':
  main()
