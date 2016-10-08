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
import json
import tempfile
import pytest
import numpy as np
import random

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'

from ndtype import IMAGE, UINT8
from params import Params
from webservices.ndwsprojingest import createJson
from postmethods import getURL, postURL, postNPZ, getNPZ
import makeunitdb
import site_to_test

SITE_HOST = site_to_test.site

p = Params()
p.token = 'unittest'
p.resolution = 0
p.channels = ['CHAN1', 'CHAN2']
p.channel_type = IMAGE
p.datatype = UINT8
p.dataset = 'unittest'

class Test_AutoIngest_Json():

  def setup_class(self):
    """Setup Parameters"""
    pass

  def teardown_class(self):
    """Teardown Parameters"""
    # makeunitdb.deleteTestDB('unittest')
    # makeunitdb.deleteTestDB('unittest2')
    # calling a different fucntion for project list as django1.9 introduced new weirdness
    makeunitdb.deleteTestDBList(['unittest','unittest2'])
  
  def test_basic_json(self):
    """Test the basic JSON project creation with only the required fields"""
    
    # dataset format = (dataset_name, [ximagesz, yimagesz, zimagesz], [[xvoxel, yvoxel, zvoxel], [xoffset, yoffset, zoffset], timerange, scalinglevels, scaling)
    dataset = (p.dataset, [2000,2000,30], [1.0,1.0,5.0], None, None, None, None)
    # project format = (project_name, token_name, public)
    project = (p.token, None, None)
    # channel format = { chan1 : (channel_name, datatype, channel_type, data_url, file_name, exceptions, resolution, windowrange, readonly), chan2: ...... }
    channels = { p.channels[0] : (p.channels[0], p.datatype, p.channel_type, 'http://localhost/data/sample_dir/', 'SLICE', 'tif', None, None, None, None) }
    metadata = { 'Author': 'Will', 'Animal':'Mouse', 'Date_Collected':'10/2/2015' }

    json_file = tempfile.NamedTemporaryFile(mode='w+b')
    json_file.write(createJson(dataset, project, channels, metadata=metadata))
    json_file.seek(0)

    # posting the JSON url and checking if it is successful
    response = json.loads(postURL("http://{}/sd/autoIngest/".format(SITE_HOST), json_file).read())
    assert('SUCCESS. The ingest process has now started.' == response)

    # fetching the JSON info
    f = getURL("http://{}/sd/{}/info/".format(SITE_HOST, p.token))

    # read the JSON file
    proj_info = json.loads(f.read())
    assert( proj_info['project']['name'] == p.token )
    assert( proj_info['dataset']['imagesize']['0'] == [2000,2000,30])
    assert( proj_info['dataset']['cube_dimension']['0'] == [128,128,16])
    assert( proj_info['dataset']['scalinglevels'] == 1)
    assert( proj_info['channels'][p.channels[0]]['resolution'] == 0)
    assert( proj_info['channels'][p.channels[0]]['datatype'] == p.datatype)
    try:
      assert( proj_info['metadata'][0]['Author'] == 'Will')
    except KeyError, AssertionError:
      print "LIMS System not working"
  
  def test_complex_json(self):
    """Test the complex JSON project creation with only the required fields"""
    
    p.token = 'unittest2'
    # dataset format = (dataset_name, [ximagesz, yimagesz, zimagesz], [[xvoxel, yvoxel, zvoxel], [xoffset, yoffset, zoffset], timerange, scalinglevels, scaling)
    dataset = (p.dataset, [2000,2000,30], [1.0,1.0,5.0], [0,0,0], None, None, None)
    # project format = (project_name, token_name, public)
    project = (p.token, None, None)
    # channel format = { chan1 : (channel_name, datatype, channel_type, data_url, file_name, exceptions, resolution, windowrange, readonly), chan2: ...... }
    channels = { p.channels[1] : (p.channels[1], p.datatype, p.channel_type, 'sample_data_url', 'sample_filename', 'tif', None, None, None, None) }
    
    json_file = tempfile.NamedTemporaryFile(mode='w+b')
    json_file.write(createJson(dataset, project, channels))
    json_file.seek(0)

    # posting the JSON url and checking if it is successful
    response = json.loads(postURL("http://{}/sd/autoIngest/".format(SITE_HOST), json_file).read())
    assert('SUCCESS. The ingest process has now started.' == response)

    # fetching the JSON info
    f = getURL("http://{}/sd/{}/info/".format(SITE_HOST, p.token))

    # read the JSON file
    proj_info = json.loads(f.read())
    assert( proj_info['project']['name'] == p.token )
    assert( proj_info['dataset']['imagesize']['0'] == [2000,2000,30])
    assert( proj_info['dataset']['cube_dimension']['0'] == [128,128,16])
    assert( proj_info['dataset']['scalinglevels'] == 1)
    assert( proj_info['channels'][p.channels[1]]['resolution'] == 0)
    assert( proj_info['channels'][p.channels[1]]['datatype'] == p.datatype)

  def test_error_json(self):
    """Test the wrong JSON project creation with only the required fields"""

    # Here we send incorrect dataset information

    # dataset format = (dataset_name, [ximagesz, yimagesz, zimagesz], [[xvoxel, yvoxel, zvoxel], [xoffset, yoffset, zoffset], timerange, scalinglevels, scaling)
    dataset = (p.dataset, [1000,2000,1000], [1.0,1.0,5.0], [0,0,0], None, None, None)
    # project format = (project_name, token_name, public)
    project = (p.token, None, None)
    # channel format = { chan1 : (channel_name, datatype, channel_type, data_url, file_name, exceptions, resolution, windowrange, readonly), chan2: ...... }
    channels = { p.channels[1] : (p.channels[1], p.datatype, p.channel_type, 'sample_data_url', 'sample_filename', None, None, None, None) }
    
    json_file = tempfile.NamedTemporaryFile(mode='w+b')
    json_file.write(createJson(dataset, project, channels))
    json_file.seek(0)

    # posting the JSON url and checking if it is successful
    response = postURL("http://{}/sd/autoIngest/".format(SITE_HOST), json_file)
    assert(response.code == 400)
    assert('Dataset {} already exists and is different then the chosen dataset. Please choose a different dataset name'.format(p.dataset) == json.loads(response.read()))
