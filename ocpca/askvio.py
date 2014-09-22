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
    dbobj.ascli = aerospike.client(ascfg).connect()


  def __del__ ( self ):
    """Close the connection"""
    self.ascli.close()


  def getCube ( self, cube, key, resolution, update ):
    """Retrieve a cube from the database by token, resolution, and key"""

    value = dbobj.ascli.get ( db.annoproj.token + ":" + str(resolution)  + ":" + str(key) )

    # If we can't find a cube, assume it hasn't been written yet
    if ( value == None ):
      cube.zeros ()
    else:
      cube.data=value

  def commit ( self ):
    """Commit the transaction.  Moved out of __del__ to make explicit.""" 
    pass


  def getCubes ( self, listofidxs ):

    for key in listofidxs:
      value = dbobj.ascli.get ( db.annoproj.token + ":" + str(resolution)  + ":" + str(key) )
      # hoew to deal with empty cubes RBTODO
      yield value

    sql = "SELECT zindex, cube FROM " + dbname + " WHERE zindex IN (%s)" 

    # creats a %s for each list element
    in_p=', '.join(map(lambda x: '%s', listofidxs))
    # replace the single %s with the in_p string
    sql = sql % in_p
    rc = self.cursor.execute(sql, listofidxs)

    yield ( self.cursor.fetchone() )


  #
  # putCube
  #
  def putCube ( self, key, resolution, cube ):
    """Store a cube from the annotation database"""

    # compress the cube
    npz = cube.toNPZ ()

    # we created a cube from zeros
    if cube.fromZeros ():

      sql = "INSERT INTO " + self.db.annoproj.getTable(resolution) +  "(zindex, cube) VALUES (%s, %s)"

      # this uses a cursor defined in the caller (locking context): not beautiful, but needed for locking
      try:
        self.cursor.execute ( sql, (key,npz))
      except MySQLdb.Error, e:
        logger.error ( "Error inserting cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise

    else:

      sql = "UPDATE " + self.db.annoproj.getTable(resolution) + " SET cube=(%s) WHERE zindex=" + str(key)
      try:
        self.cursor.execute ( sql, (npz))
      except MySQLdb.Error, e:
        logger.error ( "Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise



  def getIndex ( self, entityid, resolution, update ):
    """MySQL fetch index routine"""

    #get the block from the database                                            
    sql = "SELECT cube FROM " + self.db.annoproj.getIdxTable(resolution) + " WHERE annid\
= " + str(entityid) 
    if update==True:
       sql += " FOR UPDATE"
    try:
       self.cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.warning ("Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except BaseException, e:
       logger.exception("Unknown exception")
       raise

    row = self.cursor.fetchone ()
   
    # If we can't find a index, they don't exist                                
    if ( row == None ):
       return []
    else:
       fobj = cStringIO.StringIO ( row[0] )
       return np.load ( fobj )      


  def putIndex ( self, key, index, resolution ):
    """MySQL put index routine"""

    sql = "INSERT INTO " +  self.db.annoproj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
    
    try:
       fileobj = cStringIO.StringIO ()
       np.save ( fileobj, index )
       self.cursor.execute ( sql, (key, fileobj.getvalue()))
    except MySQLdb.Error, e:
       logger.warning("Error updating index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except BaseException, e:
       logger.exception("Unknown error when updating index")
       raise

  def updateIndex ( self, key, index, resolution ):
    """MySQL update index routine"""

    #update index in the database
    sql = "UPDATE " + self.db.annoproj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(key)
    try:
       fileobj = cStringIO.StringIO ()
       np.save ( fileobj, index )
       self.cursor.execute ( sql, (fileobj.getvalue()))
    except MySQLdb.Error, e:
       logger.warnig("Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except:
      logger.exception("Unknown exception")
      raise


  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""

    sql = "DELETE FROM " +  self.db.annoproj.getIdxTable(res)  +  " WHERE annid=" + str(annid)
    
    try:
       self.cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error("Error deleting the index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except:
      logger.exception("Unknown exception")
      raise

