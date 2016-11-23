# Copyright 2016 NeuroData (http://neurodata.io)
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
import json
import tempfile
import pytest
import numpy as np
import random
import h5py
import urllib2 
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from params import Params
from postmethods import postNPZ, getNPZ 
import makeunitdb
from ndlib.ndtype import UINT8, UINT16, UINT32, ANNOTATION, IMAGE 
import site_to_test
SITE_HOST = site_to_test.site


p = Params()
p.token = 'unittest'
p.channels = ['testchannel']
p.args = (0,1024,0,1024,1,11)

class Test_Annotation_Json():

  def setup_class(self):
    """Setup Parameters"""
    makeunitdb.createTestDB(p.token, p.channels, channel_type=ANNOTATION, channel_datatype=UINT32, public=True, ximagesize=1024, yimagesize=1024, zimagesize=10, xvoxelres=1.0, yvoxelres=1.0, zvoxelres=10.0, readonly=0)


  def teardown_class(self):
    """Teardown Parameters"""
    makeunitdb.deleteTestDB(p.token)


  def test_get_anno_by_loc(self):
    """Test the annotation (RAMON) JSON interface"""

    image_data = np.random.randint(0, high=255, size=[1, 10, 1024, 1024]).astype(np.uint32)
    response = postNPZ(p, image_data)

    assert( response.code == 200 )

    voxarray = getNPZ(p)
    # check that the return data matches
    assert( np.array_equal(voxarray, image_data) )

    # query for an ID at res0 
    res = 0
    x = 50
    y = 50
    z = 5
    cutout = '{}/{}/{}/{}/'.format( res, x, y, z ) 
    url = 'http://{}/sd/{}/{}/id/{}'.format( SITE_HOST, p.token, p.channels[0], cutout )
    
    try:
      # Build a get request
      req = urllib2.Request(url)
      response = urllib2.urlopen(req)
    except urllib2.HTTPError,e:
      print e 
      assert(e.reason == 0)
    
    assert( response.code == 200 )

    response_id = int(response.read())

    # the offset for this dataset is set to 1, hence z-1 
    assert( response_id == image_data[0, z-1, y, x] )

