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

import urllib2
import pytest
import json
import h5py
import tempfile
from contextlib import closing
from lxml import etree
import makeunitdb
from ndlib.restutil import *
from params import Params
from test_settings import *

# Test_Info
# 1 - test_public_tokens - Test the public tokens interface
# 2 - test_info - Test the json info interface
# 3 - test_projinfo - Test the hdf5 info interface
# 4 - test_reserve - Test the reserve tokens interface

p = Params()
p.token = 'unittest'
p.channels = ['unit_anno']

class Test_Info:
  """Other interfaces to NDCA that don't fit into other categories"""

  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB(p.token, public=True)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB(p.token)

  def test_public_tokens (self):
    """Test the function that shows the public tokens"""

    response = getJson("https://{}/sd/public_tokens/".format( SITE_HOST ))
    assert ( p.token in response.json() )

  def test_public_datsets (self):
    """Test the function that shows the public datasets"""

    response =  getJson("https://{}/sd/public_datasets/".format( SITE_HOST ))
    assert (p.token in response.json())

  def test_info(self):
    """Test the info query"""

    response = getJson("https://{}/sd/{}/info/".format(SITE_HOST, p.token))
    assert ( response.json()['project']['name'] == p.token )
    assert ( response.json()['channels'][p.channels[0]]['channel_type'] == 'annotation' )
    assert ( response.json()['dataset']['offset']['0'][2] == 1 )


  def test_projinfo (self):
    """Test the projinfo query"""

    f = getURL("https://{}/sd/{}/projinfo/".format(SITE_HOST, p.token))

    # read the hdf5 file
    tmpfile = tempfile.NamedTemporaryFile ()
    tmpfile.write(f.content)
    tmpfile.seek(0)
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

    assert (str(h5f['CHANNELS'][p.channels[0]]['TYPE'].value[0]) == 'annotation')
    assert (str(h5f['PROJECT']['NAME'].value[0]) == p.token)
    assert (h5f['DATASET']['OFFSET']['0'][2] == 1)

  def test_xmlinfo (self):
    """Test the projinfo query"""

    f = getURL("https://{}/sd/{}/volume.vikingxml".format(SITE_HOST, p.token))

    xmlinfo = etree.XML(f.content)
    assert( xmlinfo.values()[2] == p.token )
    assert( xmlinfo.values()[3] == '1000' )

  # def test_reserve ( self ):
    # """Reserve 1000 ids twice and make sure that the numbers work"""

    # url =  "http://{}/sd/{}/{}/reserve/{}/".format( SITE_HOST, p.token, p.channels[0], 1000 )
    # f = getURL ( url )
    # (id1, size1) = json.loads(f.content)
    # f = getURL ( url )
    # (id2, size2) = json.loads(f.content)

    # assert ( id2 - id1 == 1000 )
    # assert ( size1 == size2 == 1000 )
