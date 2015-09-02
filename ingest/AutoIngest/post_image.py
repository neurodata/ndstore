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

# Author : Kunal Lillaney
# Version : OCP_VERSION 0.7, SCHEMA_VERSION 0.7

import os
import sys
import argparse
import h5py
import urllib2
import tempfile
import numpy as np

def post_hdf5 (token_name, host_name = 'ocp.me'):
  """Post a HDF5 File"""

  # Your data goes into imageData
  # IMPORTANT : Do ensure that the posted data numpy type matches your dataset numpy type
  # Image 8 bit / Channel 8 bit = np.uint8
  # Image 16 bit / Channel 16 bit = np.uint.16

  # Here I create a 10x10x2 cube of Image data. The order which post data is zyx
  # The data in image_data[0] is the 1st channel, image_data[1] is the 2nd channel and so on
  image_data = np.uint16(range(0,20000)).reshape(2,100,100)
  # Specify your channel_list here. There should be at least one channel in this list
  channel_list = ['Grayscale', 'Blue']
  
  # Here we fill in the post args. They have xyz order
  # post_args = (resolution, xmin, xmax, ymin, ymax, zmin, zmxax)
  # Here I post the 10x10x2 cube to of data to 3000,3010/4000,4010/500,502 volume
  # Best practice is to post data in the multiples of 128,128,16
  post_args = (3000, 3100, 4100, 4200, 0, 2, 0, 10)
  
  # Create a temp file
  tmpfile = tempfile.NamedTemporaryFile()
  # Create a hdf5 file. Set the data to imageData
  f5out = h5py.File ( tmpfile.name, driver='core', backing_store=True )
  for idx, ch in enumerate(channel_list):
   changrp = f5out.create_group("{}".format(ch))
   changrp.create_dataset("{}".format('CUTOUT'), tuple(image_data[idx,:].shape), image_data[idx,:].dtype, compression='gzip', data=image_data[idx,:])
  
  f5out.close()
  tmpfile.seek(0)

  # Creating the url. The arguments here are the region you want to post the data to
  # IMPORTANT : You can only post to a project which is NOT read-only. Do ensure that when you create a token, it is not set to read-only.
  url = 'http://{}/ocpca/{}/hdf5/{}/{}/{},{}/{},{}/{},{}/'.format(host, token, ','.join(channel_list), *post_args)
  # Posting the url to the host
  post_url (url, tmp_file)
  tmp_file.close()

def post_npz (token, host='ocp.me'):
 """Post a npz file"""
 
 # Here I create a 10x10x2 cube of Image data. The order which post data is zyx
 # The data in image_data[0] is the 1st channel, image_data[1] is the 2nd channel and so on
 image_data = np.uint16(range(0,20000)).reshape(2,100,100)
 # Specify your channel_list here. There should be at least one channel in this list
 channel_list = ['Grayscale', 'Blue']
 
 # Here we fill in the post args. They have xyz order
 # post_args = (resolution, xmin, xmax, ymin, ymax, zmin, zmxax)
 # Here I post the 10x10x2 cube to of data to 3000,3010/4000,4010/500,502 volume
 # Best practice is to post data in the multiples of 128,128,16
 post_args = (3000, 3100, 4100, 4200, 0, 2, 0, 10)


def post_url (url, f):
 """Opening the url and verifying if it connects or else exit the program"""
  try:
    req = urllib2.Request ( url, f.read() )
    print "POST : {}".format(url)
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)
