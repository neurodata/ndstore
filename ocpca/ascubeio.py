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
import cStringIO
import zlib
import MySQLdb
import re
from collections import defaultdict
import itertools

import aerospike

"""Helpers function to do cube I/O in across multiple DBs.
    This file is aerospike
    This uses the state and methods of ocpcadb"""

def init ( dbobj ):
  """Connect to the database"""

  ascfg = { 'hosts': [ ('127.0.0.1', 3000) ] }
  dbobj.ascli = aerospike.client(ascfg).connect()

  def __del__ ( self ):
    """Close the connection"""
    if ASPIKE:
      self.ascli.close()


def getCube ( dbobj, cube, key, resolution, update )
  """Retrieve a cube from the database by token, resolution, and key"""

  value = dbobj.ascli.get ( dbobj.token + ":" + str(resolution)  + ":" + str(key) )

  # If we can't find a cube, assume it hasn't been written yet
  if ( value == None ):
    cube.zeros ()
  else:
    cube.data=value


