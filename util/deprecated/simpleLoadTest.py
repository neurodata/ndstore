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
import urllib2
import argparse
import time
import multiprocessing as mp

import pdb

"""

  A simple test which reads a random sized file hosted on the webserver. 

"""

def FetchFile(result):

  url = "http://{}/kunal_test/{}".format(result.host, result.filename)

  try:
    response = urllib2.urlopen(url)
    print "Success", mp.current_process()
  except urllib2.URLError,e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)

def main():

  parser = argparse.ArgumentParser(description="Run the simple test")
  parser.add_argument('host', action="store", help="Target HostName")
  parser.add_argument('filename', action="store", help="FileName")
  parser.add_argument('process', action="store", type=int, help="Processes")
  parser.add_argument('jobsize', action="store", type=int, help="Processes")
  parser.add_argument('iterations', action="store", type=int, help="Number of iterations")
  result = parser.parse_args()
  
  pdb.set_trace()

  for i in range(result.iterations):
    pool = mp.Pool(result.process)
    pool.map(FetchFile,[result]*result.process*result.jobsize)
    pool.close()
    pool.join()

if __name__ == "__main__":
  main()
