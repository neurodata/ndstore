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

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.backends.backend_pdf import PdfPages

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
x_axis_values = []

print "-----SERIALIZATION TIME-----"
for i in range(0, 4, 1):

  CUBE_VALUE = int(BASE_SIZE*math.pow(2,i))
  x_axis_values.append(CUBE_VALUE)
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


# opening a pdf file
pp = PdfPages('time_serialization.pdf')

# Time Serlization Graph

# plot values
plt.figure(figsize=(10,10))
plt.plot(x_axis_values, numpy_ts_values, color='green', marker='o')
plt.plot(x_axis_values, hdf5_ts_values, color='blue', marker='^')
plt.plot(x_axis_values, blosc_ts_values, color='red', marker='s')

# configure x-axis
plt.xlim(0,5500)
plt.xticks(x_axis_values)

# configure y-xis
plt.ylim(0,int(max(numpy_ts_values+hdf5_ts_values+blosc_ts_values))+50)
plt.yticks(range(0,int(max(numpy_ts_values+hdf5_ts_values+blosc_ts_values))+50,50))

# axis lables
plt.xlabel('Cube Sizes')
plt.ylabel('Time(seconds)')

# legend
numpy_line = mlines.Line2D([], [], color='green', marker='o', label='Numpy')
hdf5_line = mlines.Line2D([], [], color='blue', marker='^', label='HDF5')
blosc_line = mlines.Line2D([], [], color='red', marker='s', label='Blosc')
plt.legend(handles=[numpy_line, hdf5_line, blosc_line])

# title
plt.title("Serialization Times")

# show the graph
#plt.show()

# save the plot to file
pp.savefig()

# Size serialization graph

numpy_ss_values = [x/(1024*1024) for x in numpy_ss_values]
hdf5_ss_values = [x/(1024*1024) for x in hdf5_ss_values]
blosc_ss_values = [x/(1024*1024) for x in blosc_ss_values]

# plot the values
plt.figure(figsize=(10,10))
plt.plot(x_axis_values, numpy_ss_values, color='green', marker='o')
plt.plot(x_axis_values, hdf5_ss_values, color='blue', marker='^')
plt.plot(x_axis_values, blosc_ss_values, color='red', marker='s')

# configure x-axis
plt.xlim(0,5500)
plt.xticks(x_axis_values)

# configure y-xis
plt.ylim(0,1000)
plt.yticks(range(0,int(max(numpy_ss_values+hdf5_ss_values+blosc_ss_values))+100,100))

# axis lables
plt.xlabel('Cube Sizes')
plt.ylabel('Size(MB\'s)')
plt.legend(handles=[numpy_line, hdf5_line, blosc_line])

# title
plt.title("Serialization Sizes")

# save the plot to file
pp.savefig()

# Time deserialzation graph

# plot the values
plt.figure(figsize=(10,10))
plt.plot(x_axis_values, numpy_ds_values, color='green', marker='o')
plt.plot(x_axis_values, hdf5_ds_values, color='blue', marker='^')
plt.plot(x_axis_values, blosc_ds_values, color='red', marker='s')

# configure x-axis
plt.xlim(0,5500)
plt.xticks(x_axis_values)

# configure y-xis
plt.ylim(0,int(max(numpy_ds_values+hdf5_ds_values+blosc_ds_values))+50)
plt.yticks(range(0,int(max(numpy_ds_values+hdf5_ds_values+blosc_ds_values))+50,50))

# axis lables
plt.xlabel('Cube Sizes')
plt.ylabel('Time(seconds)')
plt.legend(handles=[numpy_line, hdf5_line, blosc_line])

# title
plt.title("DeSerialization Times")

# save the plot to file
pp.savefig()

# close the file
pp.close()

######################################################################################################

# Don't need

#print "Marshal Dump:", timeit.timeit('marshal.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16))', 'import marshal;import numpy as np',number=1)
#print "CPickle Dump:", timeit.timeit('pickle.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16))', 'import cPickle as pickle;import numpy as np',number=1)
#print "MsgPack Dump:", timeit.timeit('msgpack.packb(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16), default=m.encode)', 'import msgpack;import msgpack_numpy as m;import numpy as np',number=1)
#print "Marshal Dump and Load:", timeit.timeit('marshal.loads(marshal.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16)))', 'import marshal;import numpy as np',number=1)
#print "CPickle Dump and Load:", timeit.timeit('pickle.loads(pickle.dumps(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16)))', 'import cPickle as pickle;import numpy as np',number=1)
#print "MsgPack Pack and Unpack:", timeit.timeit('msgpack.unpackb(msgpack.packb(np.asarray(range(1024*1024*16), dtype=np.uint32).reshape(1024,1024,16), default=m.encode),object_hook=m.decode)', 'import msgpack;import msgpack_numpy as m;import numpy as np',number=1)
