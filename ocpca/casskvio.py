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

"""Helpers function to do cube I/O in across multiple DBs.
    This file is aerospike
    This uses the state and methods of ocpcadb"""

class CassandraKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # connect to cassandra
    self.cluster = Cluster()
    self.session = self.cluster.connect(db.annoproj.getDBName())

  def __del__ ( self ):
    """Close the connection"""
    self.session.close()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""
    pass
    
    
  def commit ( self ): 
    """Commit the transaction.  Moved out of __del__ to make explicit."""
    pass
    
  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""
    pass
    

  def getCube ( self, cube, zidx, resolution, update ):
    """Retrieve a cube from the database by token, resolution, and key"""

    cql = "SELECT cuboid FROM cuboids WHERE resolution = %s AND zidx = %s"
    row = self.session.execute ( cql, (resolution, zidx ))

    # cubes are HDF5 files
    tmpfile = tempfile.NamedTemporaryFile ()
    tmpfile.write ( row[0].cuboid.decode('hex') )
    tmpfile.seek(0)
    h5 = h5py.File ( tmpfile.name ) 

    # return the numpy array
    cube.data = np.array ( h5['cuboid'] )


  def getCubes ( self, listofidxs, resolution ):

    import pdb; pdb.set_trace()
#    cql = "SELECT cuboid FROM cuboids WHERE resolution = %s AND zidx in %s" 
    cql = "SELECT cuboid FROM cuboids WHERE resolution = %s AND zidx in %s" % (resolution, tuple(listofidxs)) 
    rows = self.session.execute ( cql )
#    rows = self.session.execute ( cql, ( resolution, tuple(listofidxs)))

    for row in rows:

      # cubes are HDF5 files
      tmpfile = tempfile.NamedTemporaryFile ()
      tmpfile.write ( row.cuboid.decode('hex') )
      tmpfile.seek(0)
      h5 = h5py.File ( tmpfile.name ) 

      # return the numpy array
#      t = np.array ( h5['cuboid'] )
      yield h5['cuboid']

  #
  # putCube
  #
  def putCube ( self, key, resolution, cube ):
    """Store a cube from the annotation database"""

    tmpfile= tempfile.NamedTemporaryFile ()
    h5t = h5py.File ( tmpfile.name )
    h5.create_dataset ( "cuboid", tuple(cube.data.shape), cube.data.dtype,
                             compression='gzip',  data=cube.data )
    h5tocass.close()
    tmpfile.seek(0)

    cql = "INSERT INTO cuboids ( resolution, zidx, cuboid ) VALUES ( %s, %s, %s )"
    session.execute ( cql, ( resolution, zidx, tmpfiletocass.read().encode('hex')))



  def getIndex ( self, annid, resolution, update ):
    """Fetch index routine.  Update is irrelevant for KV clients"""
    pass


  def putIndex ( self, annid, index, resolution ):
    """MySQL put index routine"""
    pass


  def updateIndex ( self, annid, index, resolution ):
    """MySQL update index routine"""
    pass


  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""
    pass
