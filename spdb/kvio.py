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

from abc import ABCMeta, abstractmethod

from ndtype import MYSQL, RIAK, CASSANDRA, DYNAMODB, REDIS

import logging
logger=logging.getLogger("neurodata")


class KVIO:
  # __metaclass__ = ABCMeta

  def __init__ ( self, db ):
    """Connect to the S3 backend"""
    self.db = db
    
  def close ( self ):
    """Close the connection"""
    pass

  def startTxn ( self ):
    """Start a transaction. Ensure database is in multi-statement mode."""
    pass
    
  def commit ( self ): 
    """Commit the transaction. Moved out of __del__ to make explicit."""
    pass
    
  def rollback ( self ):
    """Rollback the transaction. To be called on exceptions."""
    pass
  
  @abstractmethod
  def getCube(self, ch, zidx, resolution, update=False, timestamp=None):
    """Retrieve a single cube from the database"""
    return NotImplemented

  @abstractmethod
  def getCubes(self, ch, listofidxs, resolution, neariso=False, timestamp=None):
    """Retrieve multiple cubes from the database"""
    return NotImplemented
  
  @abstractmethod
  def getTimeCubes(self, ch, idx, listoftimestamps, resolution):
    """Retrieve multiple cubes from the database"""
    return NotImplemented
 
  @abstractmethod
  def putCube(self, ch, zidx, resolution, cubestr, update=False, timestamp=None):
    """Store a single cube into the database"""
    return NotImplemented
  
  @abstractmethod
  def putCubes(self, ch, listofidxs, resolution, listofcubes, update=False, timestamp=None):
    """Store multiple cubes into the database"""
    return NotImplemented
  
  # Factory method for KVIO Engine
  @staticmethod
  def getIOEngine(db):
    
    if db.KVENGINE == MYSQL:
      from mysqlkvio import MySQLKVIO
      db.NPZ = False
      return MySQLKVIO(db)
    elif db.KVENGINE == CASSANDRA:
      from casskvio import CassandraKVIO
      db.NPZ = True
      return CassandraKVIO(db)
    elif db.KVENGINE == RIAK:
      from riakkvio import RiakKVIO
      db.NPZ = True
      return RiakKVIO(db)
    elif db.KVENGINE == REDIS:
      from rediskvio import RedisKVIO
      db.NPZ = False
      return RedisKVIO(db)
    else:
      return KVIO(db)

