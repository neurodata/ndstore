# Copyright 2014 Open Connectome Project (http://neurodata.io)
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

from __future__ import division
import os
import sys
import numpy as np
import marshal
import h5py
import cPickle
import timeit
import zlib
import cStringIO
import tempfile
import blosc
import time
import math
import csv


sys.path += [os.path.abspath('../django/')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'

from restutil import getURL, generateURLBlosc

ITERATIONS = 6
HOST = 'openconnecto.me/ocp'
TOKEN = 'mitra14N777'
CHANNELS = ['image']
RESOLUTION = 0
OFFSET = [9000,9000,7]
BASE_SIZE = 128
Z_SIZE = 16

numpy_ts_values = []
hdf5_ts_values = []
blosc_ts_values = []
numpy_ds_values = []
hdf5_ds_values = []
blosc_ds_values = []
numpy_ss_values = []
hdf5_ss_values = []
blosc_ss_values = []
x_axis_values = []

print "-----SERIALIZATION TIME-----"

for i in range(0, ITERATIONS, 1):

  CUBE_VALUE = int(BASE_SIZE*math.pow(2,i))
  x_axis_values.append(CUBE_VALUE)
  print "SIZE:{}".format(CUBE_VALUE)
  cutout_args = (OFFSET[0], OFFSET[0]+CUBE_VALUE, OFFSET[1], OFFSET[1]+CUBE_VALUE, OFFSET[2], OFFSET[2]+Z_SIZE)
  data = blosc.unpack_array(getURL(generateURLBlosc(HOST, TOKEN, CHANNELS, RESOLUTION, cutout_args)))
  # data = np.asarray(range(CUBE_VALUE*CUBE_VALUE*Z_SIZE), dtype=np.uint32).reshape(CUBE_VALUE,CUBE_VALUE,Z_SIZE)

  # NUMPY
  start = time.time()
  fileobj = cStringIO.StringIO()
  np.save(fileobj, data)
  test = zlib.compress(fileobj.getvalue())
  numpy_ts_values.append(time.time()-start)
  # numpy_ss_values.append(sys.getsizeof(data)/sys.getsizeof(test))
  numpy_ss_values.append(sys.getsizeof(test))

  start = time.time()
  test = np.load ( cStringIO.StringIO ( zlib.decompress ( test ) ) )
  numpy_ds_values.append(time.time()-start)
  
  # HDF5
  tmpfile = tempfile.NamedTemporaryFile()
  fh5out = h5py.File(tmpfile.name, driver='core',backing_store=True)
  changrp = fh5out.create_group("TEST")
  #start = time.time()
  #changrp.create_dataset("CUTOUT2",tuple(data.shape), data.dtype, compression='lzf', data=data)
  #print "LZF", time.time()-start
  #changrp.create_dataset("CUTOUT",tuple(data.shape), data.dtype, compression='gzip', data=data, compression_opts=4)
  start = time.time()
  changrp.create_dataset("CUTOUT",tuple(data.shape), data.dtype, compression='lzf', data=data)
  fh5out.close()
  hdf5_ts_values.append(time.time()-start)
  tmpfile.seek(0)
  # hdf5_ss_values.append(sys.getsizeof(data)/sys.getsizeof(tmpfile.read()))
  hdf5_ss_values.append(sys.getsizeof(tmpfile.read()))
  tmpfile.seek(0)
  start = time.time()
  fh5in = h5py.File(tmpfile.name, driver='core', backing_store=True)
  test = np.array(fh5in['TEST']['CUTOUT'])
  hdf5_ds_values.append(time.time()-start)
  fh5in.close()
  tmpfile.close()
  
  # BLOSC
  start = time.time()
  test = blosc.pack_array(data)
  blosc_ts_values.append(time.time()-start)
  # blosc_ss_values.append(sys.getsizeof(data)/sys.getsizeof(test))
  blosc_ss_values.append(sys.getsizeof(test))
  start = time.time()
  test = blosc.unpack_array(test)
  blosc_ds_values.append(time.time()-start)

numpy_ss_values = [i/(1024*1024) for i in  numpy_ss_values]
hdf5_ss_values = [i/(1024*1024) for i in  hdf5_ss_values]
blosc_ss_values = [i/(1024*1024) for i in  blosc_ss_values]

with open('compression.csv', 'a+') as csv_file:
  csv_writer = csv.writer(csv_file, delimiter=',')
  csv_writer.writerow(["CubeSize", "Zlib", "HDF5", "Blosc"])
  csv_writer.writerows(zip(x_axis_values, numpy_ts_values, hdf5_ts_values, blosc_ts_values))

with open('decompression.csv', 'a+') as csv_file:
  csv_writer = csv.writer(csv_file, delimiter=',')
  csv_writer.writerow(["CubeSize", "Zlib", "HDF5", "Blosc"])
  csv_writer.writerows(zip(x_axis_values, numpy_ds_values, hdf5_ds_values, blosc_ds_values))

with open('compression_ratio.csv', 'a+') as csv_file:
  csv_writer = csv.writer(csv_file, delimiter=',')
  csv_writer.writerow(["CubeSize", "Zlib", "HDF5", "Blosc"])
  csv_writer.writerows(zip(x_axis_values, numpy_ss_values, hdf5_ss_values, blosc_ss_values))
