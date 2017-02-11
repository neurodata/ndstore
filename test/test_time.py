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

import random
import blosc
import numpy as np
from PIL import Image
from StringIO import StringIO
import makeunitdb
from ndlib.ndtype import TIMESERIES, UINT8, UINT16
from params import Params
from postmethods import postNPZ, getNPZ, getHDF5, postHDF5, getURL
from test_settings import *

# Test Time

# Test_Time_Slice
# 1 - test_xy
# 2 - test_yz
# 3 - test_xz
# 4 - test_xy_incorrect

# Test_Time_Post
# 1 - test_npz 
# 2 - test_npz_incorrect_region
# 3 - test_npz_incorrect_datatype
# 4 - test_hdf5
# 5 - test_hdf5_incorrect_region
# 6 - test_hdf5_incorrect_datatype
# 7 - test_npz_incorrect_channel
# 8 - test_hdf5_incorrect_channel


p = Params()
p.token = 'unittest'
p.resolution = 0
p.channels = ['TIME1', 'TIME2']
p.time = [0,100]
p.channel_type = TIMESERIES
p.datatype = UINT8
p.window = [0,500]
p.voxel = [4.0,4.0,3.0]


class Test_Time_Slice:


  def setup_class(self):

    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype, time=p.time)

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)


  def test_xy (self):
    """Test the xy slice cutout"""

    p.args = (3000,3100,4000,4100,200,201,10,12)
    time_data = np.ones( [2,2,1,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, time_data, time=True)
    assert(response.status_code == 200)

    url = "https://{}/sd/{}/{}/xy/{}/{},{}/{},{}/{}/{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[1], p.args[2], p.args[3], p.args[4], p.args[6])
    response = getURL(url)
    
    assert(response.status_code == 200)
    slice_data = np.asarray ( Image.open(StringIO(response.content)) )
    assert ( np.array_equal(slice_data, time_data[0][0][0]) )

  def test_yz (self):
    """Test the yz slice cutout"""

    p.args = (4000,4001,3000,3100,200,300,10,11)
    image_data = np.ones( [2,1,100,100,1], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data, time=True)
    assert(response.status_code == 200)

    url = "https://{}/sd/{}/{}/yz/{}/{}/{},{}/{},{}/{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[2], p.args[3], p.args[4], p.args[5], p.args[6])
    response = getURL (url)
    assert(response.status_code == 200)

    slice_data = np.asarray ( Image.open(StringIO(response.content)) )
    assert ( np.array_equal(slice_data, image_data[0][0][:75][:].reshape(75,100)) )

  def test_xz (self):
    """Test the xz slice cutout"""

    p.args = (5000,5100,2000,2001,200,300,15,16)
    image_data = np.ones( [2,1,100,1,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data, time=True)
    assert(response.status_code == 200)

    url = "https://{}/sd/{}/{}/xz/{}/{},{}/{}/{},{}/{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[1], p.args[2], p.args[4], p.args[5], p.args[6])
    response = getURL (url)
    assert(response.status_code == 200)

    slice_data = np.asarray ( Image.open(StringIO(response.content)) )
    assert ( np.array_equal(slice_data, image_data[0][0][:75][:].reshape(75,100)) )

  #def test_xy_incorrect (self):
    #"""Test the xy slice cutout with incorrect cutout arguments"""

    #p.args = (11000,11100,4000,4100,200,201)

    #url = "https://{}/sd/{}/{}/xy/{}/{},{}/{},{}/{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[1], p.args[2], p.args[3], p.args[4])
    #assert ( 404 == getURL (url) )


class Test_Time_Post:

  def setup_class(self):
    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype, time=p.time )

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)

  def test_npz (self):
    """Post npz data to correct region with correct datatype"""

    p.args = (3000,3100,4000,4100,500,510,20,24)
    # upload some image data
    image_data = np.ones ( [2,4,10,100,100], dtype=np.uint8 ) * random.randint(0,255)

    response = postNPZ(p, image_data, time=True)
    # Checking for successful post
    assert( response.status_code == 200 )
    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray,image_data) )

  def test_npz_incorrect_region (self):
    """Post npz to incorrect region"""

    p.args = (8000,9000,4000,4100,500,510,110,120)
    image_data = np.ones ( [2,10,10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data, time=True)

  def test_npz_incorrect_datatype (self):
    """Post npz data with incorrect datatype"""

    p.args = (4000,4100,5000,5100,500,510,11,18)
    # upload some image data
    image_data = np.ones ( [2,7,10,100,100], dtype=np.uint16 ) * random.randint(0,255)

    response = postNPZ(p, image_data, time=True)
    assert (response.status_code == 404)

  def test_npz_incorrect_timesize (self):
    """Post npz data with incorrect time size"""

    p.args = (8000,9000,2000,3000,410,420,15,20)
    # upload some image data
    image_data = np.ones ( [2,7,10,100,100], dtype=np.uint16 ) * random.randint(0,255)

    response = postNPZ(p, image_data, time=True)
    assert (response.status_code == 404)

  def test_hdf5 (self):
    """Post hdf5 data to correct region with correct datatype"""

    p.args = (2000,2100,4000,4100,500,510,10,15)
    # upload some image data
    image_data = np.ones ( [2,5,10,100,100], dtype=np.uint8 ) * random.randint(0,255)

    response = postHDF5(p, image_data, time=True)
    assert ( response.status_code == 200 )
    h5f = getHDF5(p, time=True)

    for idx, channel_name in enumerate(p.channels):
      assert ( np.array_equal(h5f.get(channel_name).get('CUTOUT').value, image_data[idx,:]) )

  def test_hdf5_incorrect_region (self):
    """Post hdf5 file to an incorrect region"""

    p.args = (8000,7000,4000,4100,500,510,110,115)
    image_data = np.ones ( [2,5,10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postHDF5(p, image_data, time=True)
    assert (response.status_code == 404)

  def test_hdf5_incorrect_datatype (self):
    """Post hdf5 data with incorrect datatype"""

    p.args = (6000,6100,4000,4100,500,510,50,52)
    # upload some image data
    image_data = np.empty((2,2,10,100,100))
    image_data[0,:] = np.ones ( [2,10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    image_data[1,:] = np.ones ( [2,10,100,100], dtype=np.uint16 ) * random.randint(0,255)

    response = postHDF5(p, image_data, time=True)
    assert ( response.status_code == 404 )

  def test_npz_incorrect_channel (self):
    """Post npz data with incorrect channel"""

    p.channels = p.channels + ['IMAGE3']
    image_data = np.ones ( [3,2,10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data, time=True)
    assert (response.status_code == 404)

  def test_hdf5_incorrect_channel (self):
    """Post hdf5 data with incorrect channel"""

    p.args = (5000,5100,4000,4100,500,510,50,52)
    image_data = np.ones ( [3,2,10,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postHDF5(p, image_data, time=True)
    assert (response.status_code == 404)

class Test_Time_Simple_Catmaid:

  def setup_class(self):
    p.channels = ['TIME1', 'TIME2']
    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype, xvoxelres=p.voxel[0], yvoxelres=p.voxel[1], zvoxelres=p.voxel[2], time=p.time)

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)

  def test_xy_tile(self):
    """Test a simple xy tile fetch"""

    p.args = (3072,3584,4096,4608,200,201,50,52)
    # have to use a constant here for memcache purposes
    image_data = np.ones([2,2,1,512,512], dtype=np.uint8) * 130
    response = postNPZ(p, image_data, time=True)

    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray, image_data) )
    
    # xy/z/y_z_res
    url = "https://{}/catmaid/{}/{}/xy/{}/{}/{}_{}_{}.png".format(SITE_HOST, p.token, p.channels[0], p.args[6], p.args[4], p.args[2]/512, p.args[0]/512, p.resolution)
    f = getURL (url)

    slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    assert ( np.array_equal(slice_data, image_data[0][0][0]) )

  def test_yz_tile (self):
    """Test a simple yz slice fetch"""

    p.args = (3072,3073,4096,4608,1,513,10,12)
    # have to use a constant here for memcache purposes
    image_data = np.ones([2,2,512,512,1], dtype=np.uint8) * 130
    response = postNPZ(p, image_data, time=True)

    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray, image_data) )

    # yz/x/z_y_res
    url = "https://{}/catmaid/{}/{}/yz/{}/{}/{}_{}_{}.png".format(SITE_HOST, p.token, p.channels[0], p.args[6], p.args[0], p.args[4]/512, p.args[2]/512, p.resolution)
    f = getURL (url)

    scale_range = int(512*p.voxel[2]/p.voxel[1])
    slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    assert ( np.array_equal(slice_data[:scale_range,:], image_data[0,0,:scale_range,:,0]) )

  def test_xz_tile (self):
    """Test a simple xz slice fetch"""

    p.args = (3072,3584,4096,4097,1,513,80,82)
    # have to use a constant here for memcache purposes
    image_data = np.ones([2,2,512,1,512], dtype=np.uint8) * 130
    response = postNPZ(p, image_data, time=True)

    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray, image_data) )

    # xz/y/z_x_res
    url = "https://{}/catmaid/{}/{}/xz/{}/{}/{}_{}_{}.png".format(SITE_HOST, p.token, p.channels[0], p.args[6], p.args[2], p.args[4]/512, p.args[0]/512, p.resolution)
    f = getURL (url)

    scale_range = int(512*p.voxel[2]/p.voxel[0])
    slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    assert ( np.array_equal(slice_data[:scale_range,:], image_data[0,0,:scale_range,0,:]) )

class Test_Time_Window:

  def setup_class(self):
    # Testing a different datatype now
    p.datatype = UINT16
    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype, time=p.time, window=p.window, default=True)

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)

  def test_window_default(self):
    "Test the window functionality"

    p.args = (3000,3100,4000,4100,200,201,50,52)
    image_data = np.ones([2,2,1,100,100], dtype=np.uint16) * 2000
    response = postNPZ(p, image_data, time=True)

    url = "https://{}/sd/{}/{}/xy/{}/{},{}/{},{}/{}/{}".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[1], p.args[2], p.args[3], p.args[4], p.args[6])
    f = getURL (url)

    from ndlib.windowcutout import windowCutout
    image_data = windowCutout(image_data, p.window).astype(np.uint8)
    slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    assert ( np.array_equal(slice_data, image_data[0][0][0]) )

  def test_window_args(self):
    "Test the window functionality passed as an argument"

    p.args = (3000,3100,4000,4100,200,201,20,22)
    p.window = [0,1500]
    image_data = np.ones([2,2,1,100,100], dtype=np.uint16) * 2000
    response = postNPZ(p, image_data, time=True)

    url = "https://{}/sd/{}/{}/xy/{}/{},{}/{},{}/{}/{}/window/{},{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, p.args[0], p.args[1], p.args[2], p.args[3], p.args[4], p.args[6], *p.window)
    f = getURL (url)

    from ndlib.windowcutout import windowCutout
    image_data = windowCutout(image_data, p.window).astype(np.uint8)
    slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    assert ( np.array_equal(slice_data, image_data[0][0][0]) )


class Test_Time_Diff:

  def setup_class(self):
    p.channels = ['TIME1', 'TIME2']
    p.datatype = UINT8
    makeunitdb.createTestDB(p.token, channel_list=p.channels, channel_type=p.channel_type, channel_datatype=p.datatype, time=p.time, default=True )

  def teardown_class(self):
    makeunitdb.deleteTestDB(p.token)

  def test_time_diff (self):
    """Post npz data with default channel"""

    p.args = (3000,3100,2000,2100,10,11,2,3)
    image_data1 = np.ones ( [2,1,1,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data1, time=True)
    assert (response.status_code == 200)
    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray,image_data1) )

    p.args = (3000,3100,2000,2100,10,11,3,4)
    image_data2 = np.ones ( [2,1,1,100,100], dtype=np.uint8 ) * random.randint(0,255)
    response = postNPZ(p, image_data2, time=True)
    assert (response.status_code == 200)
    voxarray = getNPZ(p, time=True)
    # check that the return matches
    assert ( np.array_equal(voxarray,image_data2) )

    p.args = (3000,3100,2000,2100,10,11,2,4)
    url = "https://{}/sd/{}/{}/diff/{}/{},{}/{},{}/{},{}/{},{}/".format(SITE_HOST, p.token, p.channels[0], p.resolution, *p.args)
    f = getURL (url)
    voxarray = blosc.unpack_array(f.content)

    image_data = np.subtract(np.float32(image_data1),np.float32(image_data2))
    assert( np.array_equal(image_data[0,:], voxarray[0,:]) )


  #def test_xy_default_channel (self):
    #"""Test the xy slice cutout"""

    #p.args = (3000,3100,4000,4100,200,201)
    #image_data = np.ones( [1,1,100,100], dtype=np.uint8 ) * random.randint(0,255)
    #response = postNPZ(p, image_data)
    #assert (response.status_code == 200)
    #voxarray = getNPZ(p)
    ## check that the return matches
    #assert ( np.array_equal(voxarray,image_data) )

    #url = "https://{}/sd/{}/xy/{}/{},{}/{},{}/{}/".format(SITE_HOST, p.token, p.resolution, p.args[0], p.args[1], p.args[2], p.args[3], p.args[4])
    #f = getURL (url)

    #slice_data = np.asarray ( Image.open(StringIO(f.content)) )
    #assert ( np.array_equal(slice_data,image_data[0][0]) )
