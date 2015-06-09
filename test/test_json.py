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

import os
import sys
import json
import tempfile
import pytest

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

from params import Params
from jsonproj import createJson
from postmethods import getURL, postURL
import makeunitdb
import site_to_test

SITE_HOST = site_to_test.site

p = Params()
p.token = 'unittest'
p.resolution = 0
p.channels = ['CHAN1']
p.channel_type = 'image'
p.datatype = 'uint8'


class Test_Json():

  def setup_class(self):

    pass

  def teardown_class(self):

    makeunitdb.deleteTestDB(p.token)
  
  def test_basic_json(self):
    """Test the basic JSON project creation with only the required fields"""

    # dataset format = (dataset_name, [ximagesz, yimagesz, zimagesz], [[xvoxel, yvoxel, zvoxel], [xoffset, yoffset, zoffset], timerange, scalinglevels, scaling)
    dataset = ('unittest_ds', [1000,1000,1000], [1.0,1.0,5.0], None, None, None, None)
    # project format = (project_name, token_name, public)
    project = (p.token, None, None)
    # channel format = { chan1 : (channel_name, datatype, channel_type, data_url, file_name, exceptions, resolution, windowrange, readonly), chan2: ...... }
    channels = { p.channels[0] : (p.channels[0], p.datatype, p.channel_type, 'sample_data_url', 'sample_filename', None, None, None, None) }
    
    json_file = tempfile.NamedTemporaryFile(mode='w+b')
    json_file.write(createJson(dataset, project, channels))
    json_file.seek(0)

    # posting the JSON url and checking if it is successful
    assert ( 200 == postURL("http://{}/ca/json/".format(SITE_HOST), json_file) )

    import pdb; pdb.set_trace()
    # fetching the JSON info
    f = getURL("http://{}/ca/{}/info/".format(SITE_HOST, p.token))

    # read the JSON file
    proj_info = json.loads(f.read())
    assert( proj_info['project']['name'] == p.token )
    assert( proj_info['dataset']['name'] == 'unittest_ds')
    assert( proj_info[''][''] == '')
    assert( proj_info[''][''] == '')
