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

import riak

"""Helpers function to do cube I/O in across multiple DBs.
    This file is aerospike
    This uses the state and methods of spatialdb"""

class RiakKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # connect to cassandra
    self.rcli = riak.RiakClient(host=db.annoproj.getKVServer(), pb_port=8087, protocol='pbc')
    self.bucket = self.rcli.bucket_type("ndspatial{}".format(db.annoproj.getDBType())).bucket(db.annoproj.getDBName())

  def close ( self ):
    """Close the connection"""
    self.rcli.close()

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
      # riak returns an object with None in the data fields if its not there
      robj = self.bucket.get( "cuboid:{}:{}".format(resolution,zidx) )
      return robj.encoded_data 
    except Exception, e:
      raise


  def getCubes ( self, listofidxs, resolution ):

    rkeys = [ "cuboid:{}:{}".format(resolution,l) for l in listofidxs ]

    try:
      robjs = self.bucket.multiget(rkeys)

      for r in robjs:
        yield re.match( "cuboid:[\d+]:(.*)", r.key).group(1), r.encoded_data

    except Exception, e:
      raise

  def putCube ( self, zidx, resolution, cubestr, udpate ):
    """Store a cube from the annotation database"""

    try:
      robj = self.bucket.new( key="cuboid:{}:{}".format(resolution,zidx), encoded_data=cubestr )
      robj.store()
    except Exception, e:
      raise


  def getIndex ( self, annid, resolution, update ):
    """Fetch index routine.  Update is irrelevant for KV clients"""

    try:
      robj = self.bucket.get( "idx:{}:{}".format(resolution,annid) )
      return robj.encoded_data 
    except Exception, e:
      raise


  def putIndex ( self, annid, resolution, indexstr, update ):
    """MySQL put index routine"""

    try:
      robj = self.bucket.new( key="idx:{}:{}".format(resolution,annid), encoded_data=indexstr )
      robj.store()
    except Exception, e:
      raise
    

  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""

    try:
      self.bucket.delete( "idx:{}:{}".format(resolution,annid) )
    except Exception, e:
      raise


  def getExceptions ( self, zidx, resolution, annid ):
    """Retrieve exceptions from the database by token, resolution, and zidx"""

    try:
      robj = self.bucket.get( "excs:{}:{}:{}".format(resolution,zidx,annid) )
      return robj.encoded_data
    except Exception, e:
      raise


  def putExceptions ( self, zidx, resolution, annid, excstr, update=False ):
    """Store exceptions in the annotation database"""

    try:
      robj = self.bucket.new( key="excs:{}:{}:{}".format(resolution,zidx,annid), encoded_data=excstr )
      robj.store()
    except Exception, e:
      raise


  def deleteExceptions ( self, zidx, resolution, annid ):
    """Delete a list of exceptions for this cuboid"""

    try:
      self.bucket.delete( "excs:{}:{}:{}".format(resolution,zidx,annid) )
    except Exception, e:
      raise

