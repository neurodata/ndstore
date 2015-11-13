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
from cassandra.cluster import Cluster

class CassandraKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # connect to cassandra
    self.cluster = Cluster( [self.db.proj.getKVServer()] )
    self.session = self.cluster.connect(self.db.proj.getDBName())
    self.session.default_timeout = 120

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
    

  def getCube(self, ch, zidx, resolution, update=False):
    """Retrieve a cube from the database by token, resolution, and zidx"""

    try:
      cql = "SELECT cuboid FROM {} WHERE resolution = {} AND zidx = {}".format(ch.getTable(resolution), resolution, zidx)
      row = self.session.execute(cql)

      if row:
        return row[0].cuboid.decode('hex')
      else:
        return None
    except Exception, e:
      pass


  def getCubes(self, ch, listofidxs, resolution, neariso=False):

    # weird pythonism for tuples of length 1 they print as (1,) and don't parse
    # just get the cube
    if len(listofidxs) == 1:
      data = self.getCube(ch, listofidxs[0], resolution, False)
      if data is None:
        return
      else:
        yield listofidxs[0], None
    else:

      try:
        # Converting the listofidxs to INT. This is wrong and needs to be fixed.
        listofidxs = [ int(i) for i in listofidxs ]
        cql = "SELECT zidx, cuboid FROM {} WHERE resolution ={} AND zidx in {}".format(ch.getTable(resolution), resolution, tuple(listofidxs)) 
        rows = self.session.execute ( cql )
        
        for row in rows:
          yield (row.zidx, row.cuboid.decode('hex'))

      except Exception, e:
        raise

  def putCube ( self, ch, zidx, resolution, cubestr, update=False ):
    """Store a cube from the annotation database"""

    try:
      cql = "INSERT INTO {} ( resolution, zidx, cuboid ) VALUES ( {}, %s, %s )".format(ch.getTable(resolution), resolution)
      self.session.execute ( cql, (zidx, cubestr.encode('hex')))
    except Exception, e:
      pass


  def getIndex ( self, ch, annid, resolution, update=False ):
    """Fetch index routine. Update is irrelevant for KV clients"""

    cql = "SELECT cuboids FROM {} WHERE annoid={} and resolution={}".format(ch.getIdxTable(resolution),annoid, resolution) 
    row = self.session.execute (cql)

    if row:
      return row[0].cuboids.decode('hex')
    else:
      return None

  def putIndex ( self, ch, annid, resolution, indexstr, update ):
    """Cassandra put index routine"""
    
    cql = "INSERT INTO {} ( resolution, annoid, cuboids ) VALUES ( {}, {}, {} )".format(ch.getIdxTable(resolution), resolution, annid, indexstr.encode('hex'))
    self.session.execute(cql)

  def deleteIndex ( self, ch, annid, resolution ):
    """Cassandra update index routine"""

    cql = "DELETE FROM {} where annoid={} and resolution={}".format(ch.getIdxTable(resolution), annid, resolution)
    self.session.execute(cql)


  def getExceptions ( self, ch, zidx, resolution, annid ):
    """Retrieve exceptions from the database by token, resolution, and zidx"""

    try:
      cql = "SELECT exceptions FROM exceptions WHERE resolution = %s AND zidx = %s and annoid=%s"
      row = self.session.execute ( cql, (resolution, zidx, annid ))
    except Exception, e:
      raise

    if row:
      return row[0].exceptions.decode('hex')
    else:
      return None

  def putExceptions ( self, ch, zidx, resolution, annid, excstr, update=False ):
    """Store exceptions in the annotation database"""

    cql = "INSERT INTO exceptions ( resolution, zidx, annoid, exceptions ) VALUES ( %s, %s, %s, %s )"
    self.session.execute ( cql, ( resolution, zidx, annid, excstr.encode('hex')))


  def deleteExceptions ( self, ch, zidx, resolution, annid ):
    """Delete a list of exceptions for this cuboid"""

    cql = "DELETE FROM exceptions WHERE resolution = %s AND zidx = %s AND annoid = %s"
    self.session.execute ( cql, ( resolution, zidx, annid))
