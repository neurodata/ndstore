# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
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
import argparse
import h5py
import urllib2
import multiprocessing as mp

import pdb

"""
  Script to Load A Server for Will's Work Load \
  Writes a given list of hdf5 Files with N processes
"""

def postH5(filename):
  """ Post a HDF5 File """
  # Creating the url
  url = 'http://{}/ocp/ocpca/{}/'.format( result.host, result.token )
  # Opening the url and verifying if it connects or else exit the program
  try:
    req = urllib2.Request ( url, open(filename).read() )
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)

def main():
  
  parser = argparse.ArgumentParser(description="Run the Load Test script")
  parser.add_argument('datalink', action="store", help='Data Folder')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Project Token')
  parser.add_argument('processes', action="store", type=int, help='Number of processes')
  parser.add_argument('batchsize', action="store", type=int, help='Number at one go')
 
  global result

  result = parser.parse_args()
  os.chdir(result.datalink)
  fileList = os.listdir(result.datalink)
  # Launching the Process Pool
  pool = mp.Pool(result.processes)
  pool.map( postH5, fileList, result.batchsize)
  pool.close()
  pool.join()

if __name__ == "__main__":
  main()
