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

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    ascfg = { 'hosts': [ ('127.0.0.1', 3000) ] }
    ascli = aerospike.client(ascfg).connect()


  def __del__ ( self ):
    """Close the connection"""
    self.ascli.close()

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
    """Retrieve a cube from the database by token, resolution, and zidx"""

    (askey, asmd, asvalue) = self.ascli.get ( self.db.annoproj.token + ":img:" + str(resolution)  + ":" + str(zidx) )

    # If we can't find a cube, assume it hasn't been written yet
    return asvalue


  def getCubes ( self, listofidxs ):

    if len(listofidxs)==1:
      yield listofidxs[0], self.ascli.get ( self.db.annoproj.token + ":img:" + str(resolution)  + ":" + str(zidx))
    for zidx in listofidxs:

      (askey, asmd, asvalue) = self.ascli.get ( self.db.annoproj.token + ":img:" + str(resolution)  + ":" + str(zidx) )
      # how to deal with empty cubes RBTODO
      yield zidx, asvalue


  #
  # putCube
  #
  def putCube ( self, zidx, resolution, cube ):
    """Store a cube from the annotation database"""

    self.ascli.put ( self.db.annoproj.token + ":img:" + str(resolution)  + ":" + str(zidx), cube.data ) 


  def getIndex ( self, annid, resolution, update ):
    """Fetch index routine.  Update is irrelevant for KV clients"""

    (askey, asmd, asvalue) = self.ascli.get ( self.db.annoproj.token + ":idx:" + str(resolution)  + ":" + str(annid) )

    # If we can't find a cube, assume it hasn't been written yet
    if ( asvalue == None ):
      return []
    else:
      return=asvalue


  def putIndex ( self, annid, index, resolution ):
    """MySQL put index routine"""

    self.ascli.put ( self.db.annoproj.token + ":idx:" + str(resolution)  + ":" + str(annid), index ) 


  def updateIndex ( self, annid, index, resolution ):
    """MySQL update index routine"""

    self.putIndex ( annid, index, resolution )


  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""

    self.ascli.remove ( self.db.annoproj.token + ":idx:" + str(resolution)  + ":" + str(annid) ) 
