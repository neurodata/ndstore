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
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'

from ingest.core.config import Configuration
from ndtype import IMAGE, UINT8, MYSQL
from params import Params
from postmethods import getJSON, postJSON, deleteJSON
import makeunitdb
import site_to_test

SITE_HOST = site_to_test.site

p = Params()
p.token = 'unittest'
p.project = 'unittest'
p.resolution = 0
p.channels = ['CHAN1', 'CHAN2']
p.channel_type = IMAGE
p.datatype = UINT8
p.dataset = 'unittest'


class Test_Ingest():

  def setup_class(self):
    """Setup Parameters"""
    makeunitdb.createTestDB(p.project, channel_list=p.channels, ximagesize=2000, yimagesize=2000, zimagesize=1000, xvoxelres=1.0, yvoxelres=1.0, zvoxelres=5.0, token_name=p.token)
  
  def teardown_class(self):
    """Teardown Parameters"""
    makeunitdb.deleteTestDB(p.project, token_name=p.token)
  
  def test_post_config(self):
    
    dataset = {
        'dataset_name' : p.dataset,
        'ximagesize': 2000,
        'yimagesize' : 2000,
        'zimagesize' : 100,
        'xvoxelres' : 1.0,
        'yvoxelres' : 2.0,
        'zvoxelres' : 1.0,
        'public' : 1
    }
    response = postJSON('http://{}/resource/dataset/{}/'.format(SITE_HOST, p.dataset), dataset)
    assert(response.status_code == 200)
