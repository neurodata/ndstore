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

import numpy as np
import cStringIO
import zlib
import urllib2
import h5py
import tempfile
import random

import makeunitdb
from params import Params
import kvengine_to_test
import site_to_test
SITE_HOST = site_to_test.site


# Test Image and Channel Project Post Methods

# Image Project Test
# TestImagePost
# test_npz - Post npz 8-bit data to Image8 Project
# test_npz_incorrect_datatype - Post npz 16-bit data to Image8 Project. Should throw 404
# test_hdf5 - Post hdf5 8-bit data to Image8 Project
# test_hdf5_incorrect_datatype - Post hdf5 16-bit data to Image8 Project. Should throw 404

# Channel Project Test
# TestChannelPost
# test_npz - Post hdf5 16-bit data to Channel16 Project. 2 Channels(Grayscale,Blue)
# test_npz_incorrect_datatype - Post hdf5 8-bit to Channel16 Project. Should throw 404
# test_npz_incorrect_channel - Post npz 16-bit data with incorrect channel name. Should throw 404
# test_npz_incorrect_number_channel - Post npz 16-bit data with less number of channels. Should throw 404
# test_hdf5 - Post 16-bit data. 2 Channels(Grayscale,Blue)
# test_hdf5_incorrect_datatype - Post hdf5 8-bit data to Channel16 Project. Should throw 404
# test_hdf5_incorrect_channel - Post hdf5 16-bit data with incorrect channel name. Should throw 404
# test_hdf5_incorrect_number_channel - Post hdf5 16-bit data with less number of channels. Should throw 404


class TestImagePost:

  def setup_class(self):

    makeunitdb.createTestDB('unittest_rw', channel_list=['IMAGE','IMAGE2'], channel_type='image', channel_datatype='uint8' )

  def teardown_class(self):

    makeunitdb.deleteTestDB('unittest_rw')

  def test_npz (self):

    p = Params()
    p.token = "unittest_rw"
    p.baseurl = SITE_HOST
    p.resolution = 0
    p.channels = ['IMAGE','IMAGE2']
    p.args = (3000,3100,4000,4100,500,510)
    
    # upload some image data
    imagedata = np.ones ( [2,10,100,100], dtype=np.uint8 ) * random.randint(0,255)

    url = 'http://{}/ca/{}/npz/{}/{}/{},{}/{},{}/{},{}/'.format ( p.baseurl, p.token, ','.join(p.channels), p.resolution, *p.args )

    fileobj = cStringIO.StringIO ()
    np.save (fileobj, imagedata)
    cdz = zlib.compress (fileobj.getvalue())

    # Build a post request
    req = urllib2.Request(url,cdz)
    response = urllib2.urlopen(req)

    # Get the image back
    f = urllib2.urlopen (url)
    rawdata = zlib.decompress (f.read())
    fileobj = cStringIO.StringIO (rawdata)
    voxarray = np.load (fileobj)

    # check that the return matches
    assert ( np.array_equal(voxarray,imagedata) )

  def test_npz_incorrect_datatype (self):

    p = Params()
    p.token = "unittest_rw"
    p.baseurl = SITE_HOST
    p.resolution = 0
    p.channel = 'IMAGE'
    p.args = (4000,4100,5000,5100,500,510)
    
    # upload some image data
    imagedata = np.ones ( [1,10,100,100], dtype=np.uint16 ) * random.randint(0,255)

    url = 'http://{}/ca/{}/npz/{}/{}/{},{}/{},{}/{},{}/'.format ( p.baseurl, p.token, p.channel, p.resolution, *p.args )

    fileobj = cStringIO.StringIO ()
    np.save (fileobj, imagedata)
    cdz = zlib.compress (fileobj.getvalue())

    # Build a post request
    try:
      req = urllib2.Request(url,cdz)
      response = urllib2.urlopen(req)
    except urllib2.HTTPError,e:
      assert (e.code == 404)


  def test_hdf5 (self):

    p = Params()
    p.token = "unittest_rw"
    p.baseurl = SITE_HOST
    p.resolution = 0
    p.channels = ['IMAGE','IMAGE2']
    p.args = (2000,2100,4000,4100,500,510)

    # upload some image data
    imagedata = np.ones ( [10,100,100], dtype=np.uint8 ) * random.randint(0,255)

    url = 'http://{}/ca/{}/hdf5/{}/{}/{},{}/{},{}/{},{}/'.format ( p.baseurl, p.token, ','.join(p.channels), p.resolution, *p.args )

    tmpfile = tempfile.NamedTemporaryFile ()
    fh5out = h5py.File ( tmpfile.name )
    for channel_name in p.channels:
      fh5out.create_dataset ( channel_name, tuple(imagedata.shape), imagedata.dtype, compression='gzip', data=imagedata )
    fh5out.close()
    tmpfile.seek(0)
    
    # Build a post request
    req = urllib2.Request(url,tmpfile.read())
    response = urllib2.urlopen(req)

    # Get the image back
    f = urllib2.urlopen (url)
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( f.read() )
    tmpfile.seek(0)
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

    for channel_name in p.channels:
      assert ( np.array_equal(h5f.get(channel_name).get('CUTOUT').value,imagedata) )

  def test_hdf5_incorrect_datatype (self):

    p = Params()
    p.token = "unittest_rw"
    p.baseurl = SITE_HOST
    p.resolution = 0
    p.channels = ['IMAGE','IMAGE2']
    p.args = (6000,6100,4000,4100,500,510)

    # upload some image data
    imagedata = np.empty((2,10,100,100))
    imagedata[0,:] = np.ones ( [10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    imagedata[1,:] = np.ones ( [10,100,100], dtype=np.uint16 ) * random.randint(0,255)

    url = 'http://{}/ca/{}/hdf5/{}/{}/{},{}/{},{}/{},{}/'.format ( p.baseurl, p.token, ','.join(p.channels), p.resolution, *p.args )

    tmpfile = tempfile.NamedTemporaryFile ()
    fh5out = h5py.File ( tmpfile.name )
    for idx,channel_name in enumerate(p.channels):
      fh5out.create_dataset ( channel_name, tuple(imagedata[idx,:].shape), imagedata[idx,:].dtype, compression='gzip', data=imagedata[idx,:] )
    fh5out.close()
    tmpfile.seek(0)
    
    # Build a post request
    try:
      req = urllib2.Request(url,tmpfile.read())
      response = urllib2.urlopen(req)
    except urllib2.HTTPError,e:
      assert (e.code == 404)
