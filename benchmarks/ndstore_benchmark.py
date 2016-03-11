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
import sys
import random
import argparse
import numpy as np
import multiprocessing
import time
import json
from operator import add, sub, mul
from functools import reduce

sys.path += [os.path.abspath('../django/')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'

from ndlib import MortonXYZ
from restutil import getURL, getURLTimed, generateURLBlosc


class BenchmarkTest:

  def __init__(self, result):
    """Init"""

    self.host = result.server_name
    self.token = result.token_name
    self.channels = [result.channel_name]
    self.resolution = result.res_value
    self.getProjInfo()
    self.fetch_list = []


  def readTest(self, start_value, number_iterations):
    """Generate the URL for read test"""

    min_values = [xmin,ymin,zmin] = map(add, self.offset, start_value)
    max_values = map(add, min_values, self.dim)
    range_args = [None]*(len(min_values)+len(max_values))
    
    for i in range(0, number_iterations, 1):
      if all([a<b for a,b in zip(max_values, self.imagesize)]):
        range_args[::2] = min_values
        range_args[1::2] = max_values
        # print "Size", reduce(mul, map(sub, max_values, min_values), 1)*2.0/(1024*1024)
        self.fetch_list.append(generateURLBlosc(self.host, self.token, self.channels, self.resolution, range_args))
        # min_values = max_values
        # max_values = map(add, map(sub, min_values, temp_values), min_values)
        min_values[2] = max_values[2]
        max_values[2] = min_values[2] + self.dim[2] 
        max_values[(i+1)%2] = start_value[(i+1)%2] + (max_values[(i+1)%2]-min_values[(i+1)%2])*2
      else:
        break

  def multiThreadTest(self, start_value, number_iterations, number_of_processes):
    """Generate the URL for multi-thread test"""

    # min_values = [xmin,ymin,zmin] = map(add, self.offset, start_value)
    min_values = [xmin, ymin, zmin] = self.offset
    max_values = map(add, min_values, self.dim)
    range_args = [None]*(len(min_values)+len(max_values))
    size_args = [None]*(len(min_values)+len(max_values))
    
    # determine the size of the cutout
    for i in range(0, number_iterations, 1):
      if all([a<b for a,b in zip(max_values, self.imagesize)]):
        size_args[::2] = min_values
        size_args[1::2] = max_values
        # increase in x,y
        max_values[(i+1)%2] = (max_values[(i+1)%2]-min_values[(i+1)%2])*2
      else:
        break
    
    # intialize the range args
    range_args[:] = size_args[:]
    range_args[::2] = map(add, start_value, size_args[::2])
    range_args[1::2] = map(add, start_value, size_args[1::2])
    
    # creating a fetch list for each process
    for i in range(0, number_of_processes, 1):
      # checking if the x,y,z dimensions are exceeded
      if all([a<b for a,b in zip(range_args[1::2], self.imagesize)]):
        self.fetch_list.append(generateURLBlosc(self.host, self.token, self.channels, self.resolution, range_args))
        # checking if this exceeds the x,y image size
        if all([a<b for a,b in zip(map(add, range_args[1:-1:2], size_args[1:-1:2]), self.imagesize)]): 
          range_args[0:-2:2] = range_args[1:-1:2]
          range_args[1:-1:2]  = map(add, range_args[1:-1:2], size_args[1:-1:2])
        # if you cannot expand more in x,y then expand in z
        elif range_args[-1] < self.imagesize[-1]:
          range_args[-2] = range_args[-1]
          range_args[-1] = range_args[-1] + size_args[-1]
        else:
          break
      else:
        break


  def getProjInfo(self):
    """Get the project info"""

    info = json.loads(getURL('http://{}/ca/{}/info'.format(self.host, self.token)))
    self.dim = info['dataset']['cube_dimension'][str(self.resolution)]
    self.imagesize = info['dataset']['imagesize'][str(self.resolution)]
    self.offset = info['dataset']['offset'][str(self.resolution)]


def main():
  """Take in the arguments"""

  parser = argparse.ArgumentParser(description='Run the Benchmark script')
  parser.add_argument("token_name", action="store", type=str, help="Token Name")
  parser.add_argument("channel_name", action="store", type=str, help="Channel Name")
  parser.add_argument("res_value", action="store", type=int, help="Resolution")
  parser.add_argument("--server", dest="server_name", action="store", type=str, default="localhost/ndstore", help="Server Name")
  parser.add_argument('--offset', dest="offset_value", nargs=3, action="store", type=int, metavar=('X','Y','Z'), default=[0,0,0], help='Start Offset')
  parser.add_argument("--num", dest="number_of_processes", action="store", type=int, default=1, help="Number of Processes")
  parser.add_argument("--iter", dest="number_of_iterations", action="store", type=int, default="1", help="Number of Iterations")


  result = parser.parse_args()
 
  bt = BenchmarkTest(result)
  if result.number_of_processes == 1:
    bt.readTest(result.offset_value, result.number_of_iterations)
  else:
    bt.multiThreadTest(result.offset_value, result.number_of_iterations, result.number_of_processes)

  from pprint import pprint
  pprint(bt.fetch_list)

  p = multiprocessing.Pool(result.number_of_processes)
  p.map(getURLTimed, bt.fetch_list)

if __name__ == '__main__':
  main()
