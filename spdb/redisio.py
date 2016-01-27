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

import redis
import blosc
import hashlib
from sets import Set
from operator import add, sub, mul, div, mod

import ndlib

SUPERCUBESIZE = [4,4,4]

import logging
logger=logging.getLogger("neurodata")


"""Helpers function to do cube I/O in across multiple DBs.
    This uses the state and methods of spatialdb"""

class RedisIO:

  def __init__ ( self, db ):
    """Connect to the S3 backend"""
    
    self.db = db
    self.client = redis.StrictRedis(host=self.db.proj.getDBHost(), port=6379, db=0)
    self.pipe = self.client.pipeline(transaction=False)
    
  
  def getCube(self, ch, zidx, timestamp, resolution, update=False, timestamp=None):
    """Retrieve a single cube from the database"""
    return   
  
  def getCubes(self, ch, listofidxs, resolution, neariso=False, timestamp=None):
    """Retrieve multiple cubes from the database"""
    self.client.mget(
    return
 
  def putCubes(self, ch, listofidxs, resolution, listofcubes, update=False, timestamp=None):
    """Store multiple cubes into the database"""
    return
  
  def putCube(self, ch, zidx, timestamp, resolution, cubestr, update=False, timestamp=None):
    """Store a single cube into the database"""
    return
