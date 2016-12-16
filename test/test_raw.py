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

import numpy as np
import makeunitdb
from ndlib.ndtype import IMAGE, UINT8, UINT16
from params import Params
from postmethods import postNPZ, getRAW
import site_to_test
SITE_HOST = site_to_test.site


# Test_RAW
# 1 - test_get_raw

p = Params()
p.token = 'unittest'
p.resolution = 0
p.channels = ['IMAGE1', 'IMAGE2']
p.window = [0,500]
p.channel_type = IMAGE
p.datatype = UINT8
p.voxel = [4.0,4.0,3.0]


class Test_Raw:

  def setup_class(self):

    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype)

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)


  def test_get_raw (self):
    """Test the xyz cube cutout"""

    p.args = (3000, 3003, 4000, 4003, 200, 203)
    image_data = (np.random.rand(2, 3, 3, 3) * 255).astype(np.uint8)
    response = postNPZ(p, image_data)
    requested_data = getRAW(p)
    requested_data.shape = (2, 3, 3, 3)

    assert ( np.array_equal(image_data, requested_data) )
