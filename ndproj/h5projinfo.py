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

import h5py
import numpy as np
from ndlib.ndtype import READONLY_FALSE, EXCEPTION_FALSE
import logging
logger = logging.getLogger("neurodata")


def h5ProjInfo ( proj, h5f ):
  """Populate the HDF5 file with project attributes"""
  
  projgrp = h5f.create_group ( 'PROJECT' )
  projgrp.create_dataset("NAME", (1,), dtype=h5py.special_dtype(vlen=str), data=proj.project_name)
  projgrp.create_dataset("HOST", (1,), dtype=h5py.special_dtype(vlen=str), data=proj.host)
  projgrp.create_dataset("ND_VERSION", (1,), dtype=h5py.special_dtype(vlen=str), data=proj.nd_version)
  projgrp.create_dataset("SCHEMA_VERSION", (1,), dtype=h5py.special_dtype(vlen=str), data=proj.schema_version)
  #projgrp.create_dataset ( "DATAURL", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._overlayserver )
  #projgrp.create_dataset ( "KNENGINE", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._kvserver )
  #projgrp.create_dataset ( "KVSERVER", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._kvengine )


def h5DatasetInfo ( dataset, h5f ):
  """Populate the HDF5 with db configuration information"""

  dsgrp = h5f.create_group('DATASET')
  dsgrp.create_dataset('NAME', (1,), dtype=h5py.special_dtype(vlen=str), data=dataset.dataset_name)
  dsgrp.create_dataset('RESOLUTIONS', data=dataset.resolutions)
  imggrp = dsgrp.create_group('IMAGE_SIZE')
  for k,v in dataset.image_size.iteritems():
    imggrp.create_dataset ( str(k), data=v )
  imggrp = dsgrp.create_group('OFFSET')
  for k,v in dataset.offset.iteritems():
    imggrp.create_dataset ( str(k), data=v )
  imggrp = dsgrp.create_group('VOXELRES')
  for k,v in dataset.voxelres.iteritems():
    imggrp.create_dataset ( str(k), data=v )
  cdgrp = dsgrp.create_group('CUBE_DIMENSION')
  for k,v in dataset.cubedim.iteritems():
    cdgrp.create_dataset ( str(k), data=v )


def h5ChannelInfo (proj, h5f):
  """Populate the HDF5 file with chanel information"""

  chgrp = h5f.create_group('CHANNELS')

  for ch in proj.projectChannels():

    changrp = chgrp.create_group(ch.channel_name)
    changrp.create_dataset('NAME', (1,), dtype=h5py.special_dtype(vlen=str), data=ch.channel_name)
    changrp.create_dataset("TYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=ch.channel_type)
    changrp.create_dataset("DATATYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=ch.channel_datatype)
    changrp.create_dataset("RESOLUTION", (1,), dtype=np.uint8, data=ch.resolution)
    changrp.create_dataset("READONLY", (1,), dtype=bool, data=(False if ch.readonly == READONLY_FALSE else True))
    changrp.create_dataset("EXCEPTIONS", (1,), dtype=bool, data=(False if ch.exceptions == EXCEPTION_FALSE else True))
    changrp.create_dataset("PROPAGATE", (1,), dtype=np.uint8, data=ch.propagate)
    changrp.create_dataset("DEFAULT", (1,), dtype=bool, data=ch.default)
    changrp.create_dataset("WINDOWRANGE", data=ch.window_range)
    changrp.create_dataset("TIMERANGE", data=ch.time_range)


def h5Info (proj, h5f):
  """Wrapper for the parts"""

  h5ProjInfo(proj, h5f)
  h5DatasetInfo(proj.datasetcfg, h5f)
  h5ChannelInfo(proj, h5f)
