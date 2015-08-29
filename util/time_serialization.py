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
import numpy as np
import marshal
import h5py
import cPickle
import msgpack
import msgpack_numpy as m
import timeit
import zlib
import cStringIO
import tempfile
import blosc
import time
import math

BASE_SIZE = 512
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

print "-----SERIALIZATION TIME-----"
for i in range(0, 1, 1):

  CUBE_VALUE = int(BASE_SIZE*math.pow(2,i))
  print "SIZE:{}".format(CUBE_VALUE)
  data = np.asarray(range(CUBE_VALUE*CUBE_VALUE*Z_SIZE), dtype=np.uint32).reshape(CUBE_VALUE,CUBE_VALUE,Z_SIZE)
  
  # NUMPY
  start = time.time()
  fileobj = cStringIO.StringIO()
  np.save(fileobj, data)
  test = zlib.compress(fileobj.getvalue())
  numpy_ts_values.append(time.time()-start)
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
  blosc_ss_values.append(sys.getsizeof(test))
  start = time.time()
  test = blosc.unpack_array(test)
  blosc_ds_values.append(time.time()-start)


######################################################################################################

# Don't need

#print "Marshal Dump:", timeit.timeit('marshal.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16))', 'import marshal;import numpy as np',number=1)
#print "CPickle Dump:", timeit.timeit('pickle.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16))', 'import cPickle as pickle;import numpy as np',number=1)
#print "MsgPack Dump:", timeit.timeit('msgpack.packb(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16), default=m.encode)', 'import msgpack;import msgpack_numpy as m;import numpy as np',number=1)
#print "Marshal Dump and Load:", timeit.timeit('marshal.loads(marshal.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16)))', 'import marshal;import numpy as np',number=1)
#print "CPickle Dump and Load:", timeit.timeit('pickle.loads(pickle.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16)))', 'import cPickle as pickle;import numpy as np',number=1)
#print "MsgPack Pack and Unpack:", timeit.timeit('msgpack.unpackb(msgpack.packb(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16), default=m.encode),object_hook=m.decode)', 'import msgpack;import msgpack_numpy as m;import numpy as np',number=1)
