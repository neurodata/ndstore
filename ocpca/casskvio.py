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
import tempfile
import h5py
#from cassandra.cluster import Cluster

"""Helpers function to do cube I/O in across multiple DBs.
    This file is aerospike
    This uses the state and methods of ocpcadb"""

class CassandraKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # connect to cassandra
    # maybe have multiple names in self.kVENginge todo
    self.cluster = Cluster( [db.annoproj.getKVServer()] )
    self.session = self.cluster.connect(db.annoproj.getDBName())

  def close ( self ):
    """Close the connection"""
    self.cluster.shutdown()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""
    pass
    
    
  def commit ( self ): 
    """Commit the transaction.  Moved out of __del__ to make explicit."""
    pass
    
  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""
    pass
    

  def getCube ( self, zidx, resolution, update ):
    """Retrieve a cube from the database by token, resolution, and zidx"""

    try:
      cql = "SELECT cuboid FROM cuboids WHERE resolution = %s AND zidx = %s"
      row = self.session.execute ( cql, (resolution, zidx ))

      if row:
        return row[0].cuboid.decode('hex')
      else:
        return None
    except Exception, e:
      pass


  def getCubes ( self, listofidxs, resolution ):

    # weird pythonism for tuples of length 1 they print as (1,) and don't parse
    # just get the cube
    if len(listofidxs)==1:
      yield listofidxs[0], self.getCube(listofidxs[0], resolution, False)
    else:

      try:
        cql = "SELECT zidx, cuboid FROM cuboids WHERE resolution = %s AND zidx in %s" % (resolution, tuple(listofidxs)) 
        rows = self.session.execute ( cql )

        for row in rows:
          yield (row.zidx, row.cuboid.decode('hex'))

      except Exception, e:
        raise

  #
  # putCube
  #
  def putCube ( self, zidx, resolution, cubestr, udpate ):
    """Store a cube from the annotation database"""

    try:
      cql = "INSERT INTO cuboids ( resolution, zidx, cuboid ) VALUES ( %s, %s, %s )"
      self.session.execute ( cql, ( resolution, zidx, cubestr.encode('hex')))
    except Exception, e:
      pass


  def getIndex ( self, annid, resolution, update ):
    """Fetch index routine.  Update is irrelevant for KV clients"""

    cql = "SELECT cuboids FROM indexes WHERE annoid=%s and resolution=%s" 
    row = self.session.execute ( cql, (annid, resolution ))

    if row:
      return row[0].cuboids.decode('hex')
    else:
      return None

  # RBTODO change name from cuboids to indexes
  def putIndex ( self, annid, resolution, indexstr, update ):
    """MySQL put index routine"""
    
    cql = "INSERT INTO indexes ( resolution, annoid, cuboids ) VALUES ( %s, %s, %s )"
    self.session.execute ( cql, ( resolution, annid, indexstr.encode('hex')))

  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""

    cql = "DELETE FROM indexes where annoid=%s and resolution=%s"
    self.session.execute ( cql, ( annid, resolution))


  def getExceptions ( self, zidx, resolution, annid ):
    """Retrieve exceptions from the database by token, resolution, and zidx"""

    cql = "SELECT exceptions FROM exceptions WHERE resolution = %s AND zidx = %s and annoid=%s"
    row = self.session.execute ( cql, (resolution, zidx, annid ))

    if row:
      return row[0].exceptions.decode('hex')
    else:
      return None

  def putExceptions ( self, zidx, resolution, annid, excstr, update=False ):
    """Store exceptions in the annotation database"""

    cql = "INSERT INTO exceptions ( resolution, zidx, annoid, exceptions ) VALUES ( %s, %s, %s, %s )"
    self.session.execute ( cql, ( resolution, zidx, annid, excstr.encode('hex')))


  def deleteExceptions ( self, zidx, resolution, annid ):
    """Delete a list of exceptions for this cuboid"""

    cql = "DELETE FROM exceptions WHERE resolution = %s AND zidx = %s AND annoid = %s"
    self.session.execute ( cql, ( resolution, zidx, annid))


