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
import tempfile
import h5py
import urllib2
import zlib
import cStringIO
import blosc
import time

sys.path += [os.path.abspath('../django/')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ocpblaze.settings'

from ndlib import MortonXYZ
from params import Params

p = Params()
p.token = "blaze"
p.resolution = 0
p.channels = ['image']
p.window = [0,0]
p.channel_type = "image"
p.datatype = "uint32"
SIZE = 1024
ZSIZE = 16

def generateURL(zidx):
  """Run the Benchmark."""

  i = zidx
  [x,y,z] = MortonXYZ(i)
  p.args = (x*SIZE, (x+1)*SIZE, y*SIZE, (y+1)*SIZE, z*ZSIZE, (z+1)*ZSIZE)
  image_data = np.ones([1,ZSIZE,SIZE,SIZE], dtype=np.uint32) * random.randint(0,255)
  return postBlosc(p, image_data)

def generateURL2(zidx):
  [x,y,z] = MortonXYZ(zidx)
  p.args = (x*SIZE, (x+1)*SIZE, y*SIZE, (y+1)*SIZE, z*ZSIZE, (z+1)*ZSIZE)
  return 'http://{}/{}/{}/blosc/{}/{},{}/{},{}/{},{}/'.format(SITE_HOST, p.token, ','.join(p.channels), p.resolution, *p.args)

def postBlosc(p, post_data):
  """Post data using the blosc interface"""

  # Build the url and then create a hdf5 object
  url = 'http://{}/{}/{}/blosc/{}/{},{}/{},{}/{},{}/'.format(SITE_HOST, p.token, ','.join(p.channels), p.resolution, *p.args)
  return (url, blosc.pack_array(post_data))


def postHDF5 (p, post_data):
  """Post data using the hdf5 interface"""

  # Build the url and then create a hdf5 object
  url = 'http://{}/{}/{}/hdf5/{}/{},{}/{},{}/{},{}/'.format(SITE_HOST, p.token, ','.join(p.channels), p.resolution, *p.args)

  tmpfile = tempfile.NamedTemporaryFile ()
  fh5out = h5py.File ( tmpfile.name )
  for idx, channel_name in enumerate(p.channels):
    chan_grp = fh5out.create_group(channel_name)
    chan_grp.create_dataset("CUTOUT", tuple(post_data[idx,:].shape), post_data[idx,:].dtype, compression='gzip', data=post_data[idx,:])
    chan_grp.create_dataset("CHANNELTYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=p.channel_type)
    chan_grp.create_dataset("DATATYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=p.datatype)
  fh5out.close()
  tmpfile.seek(0)
  return (url, tmpfile.read()) 

def postNPZ (p, post_data):
  """Post data using the npz interface"""
  
  # Build the url and then create a npz object
  url = 'http://{}/{}/{}/npz/{}/{},{}/{},{}/{},{}/'.format(SITE_HOST, p.token, ','.join(p.channels), p.resolution, *p.args)

  fileobj = cStringIO.StringIO ()
  np.save (fileobj, post_data)
  cdz = zlib.compress (fileobj.getvalue())
  return (url, cdz)

def postURLHelper(args):
  """Wrapper around postURL for mulitple arguments"""
  postURL(*args)

def postURL(url, post_data):
  """Post data"""

  try:
    # Build a post request
    req = urllib2.Request(url, post_data)
    start = time.time() 
    response = urllib2.urlopen(req)
    print time.time()-start
    return response
  except urllib2.HTTPError, e:
    return e

def getURL(url):
  """Get data"""

  try:
    # Build a get request
    req = urllib2.Request(url)
    start = time.time()
    response = urllib2.urlopen(req)
    print time.time()-start
    return response.read()
  except urllib2.HTTPError, e:
    return e

def main():
  """Take in the arguments"""

  parser = argparse.ArgumentParser(description='Run the Benchmark script')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('number_iterations', action="store", type=int, help='Number of iterations')
  parser.add_argument('number_processes', action="store", type=int, help='Number of processes')

  result = parser.parse_args()

  global SITE_HOST
  SITE_HOST = result.host
  zidx_list = range(result.number_iterations)
  random.shuffle(zidx_list)
  post_list = []
  for zidx in zidx_list:
    post_list.append(generateURL(zidx))
  from multiprocessing import Pool
  pool = Pool(result.number_processes)
  start = time.time()
  pool.map(postURLHelper, post_list)
  print time.time() - start

  # KL TODO insert get data here
  getURL(generateURL2(zidx_list[0]))
  getURL(generateURL2(zidx_list[0]))

if __name__ == '__main__':
  main()
