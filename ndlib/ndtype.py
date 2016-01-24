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

import numpy as np

# ND_CONSTANTS
IMAGE = 'image'
ANNOTATION = 'annotation'
TIMESERIES = 'timeseries'
OLDCHANNEL = 'oldchannel'
UINT8 = 'uint8'
UINT16 = 'uint16'
UINT32 = 'uint32'
UINT64 = 'uint64'
FLOAT32 = 'float32'
MYSQL = 'MySQL'
CASSANDRA = 'Cassandra'
RIAK = 'riak'
DYNAMODB = 'dynamodb'

# ND Version
ND_VERSION = '0.7'
SCHEMA_VERSION = '0.7'

ND_channeltypes = {0:IMAGE,1:ANNOTATION,2:TIMESERIES,3:OLDCHANNEL}

# channeltype groups
IMAGE_CHANNELS = [ IMAGE, OLDCHANNEL ]
TIMESERIES_CHANNELS = [ TIMESERIES ]
ANNOTATION_CHANNELS = [ ANNOTATION ]

# datatype groups
DTYPE_uint8 = [ UINT8 ]
DTYPE_uint16 = [ UINT16 ]
DTYPE_uint32 = [ UINT32 ]
DTYPE_uint64 = [ UINT64 ]
DTYPE_float32 = [ FLOAT32 ]
ND_dtypetonp = {UINT8:np.uint8, UINT16:np.uint16, UINT32:np.uint32, UINT64:np.uint64, FLOAT32:np.float32}

# Server Map
ND_servermap = {'dsp061.pha.jhu.edu':'172.23.253.61', 'dsp062.pha.jhu.edu':'172.23.253.62', 'dsp063.pha.jhu.edu':'172.23.253.63', 'localhost':'localhost'}

# Propagated Values
PROPAGATED = 2
UNDER_PROPAGATION = 1
NOT_PROPAGATED = 0

# ReadOnly Values
READONLY_TRUE = 1
READONLY_FALSE = 0

# SCALING OPTIONS
ZSLICES = 0
ISOTROPIC = 1
ND_scalingtoint = {'zslices':ZSLICES, 'xyz':ISOTROPIC}

# Exception Values
EXCEPTION_TRUE = 1
EXCEPTION_FALSE = 0

# Public Values
PUBLIC_TRUE = 1
PUBLIC_FALSE = 0
