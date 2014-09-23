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

import logging
logger=logging.getLogger("ocp")


"""Helpers function to do cube I/O in across multiple DBs.
    This uses the state and methods of ocpcadb"""

class MySQLKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # Connection info 
    try:
      self.conn = MySQLdb.connect (host = self.db.annoproj.getDBHost(),
                            user = self.db.annoproj.getDBUser(),
                            passwd = self.db.annoproj.getDBPasswd(),
                            db = self.db.annoproj.getDBName())

    except MySQLdb.Error, e:
      self.conn = None
      logger.error("Failed to connect to database: %s, %s" % (dbobj.annoproj.getDBHost(), dbobj.annoproj.getDBName()))
      raise

    # start with no cursor
    self.txncursor = None

  def __del__ ( self ):
    """Close the connection"""
    if self.conn:
      self.conn.close()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""

    self.txncursor = self.conn.cursor()
    sql = "START TRANSACTION"
    self.txncursor.execute ( sql )

  def commit ( self ):
    """Commit the transaction.  Moved out of __del__ to make explicit.""" 
    self.conn.commit()
    self.txncursor.close()
    self.txncursor = None

  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""

    self.conn.rollback()
    self.txncursor.close()
    self.txncursor = None

  def __del__ ( self ):
    """Close the connection"""
    if self.conn:
      self.conn.close()

  def getCube ( self, cube, key, resolution, update ):
    """Retrieve a cube from the database by token, resolution, and key"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    sql = "SELECT cube FROM " + self.db.annoproj.getTable(resolution) + " WHERE zindex = " + str(key) 
    if update==True:
          sql += " FOR UPDATE"

    try:
      cursor.execute ( sql )
      row = cursor.fetchone()
    except MySQLdb.Error, e:
      logger.error ( "Failed to retrieve data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()


    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      cube.zeros ()
    else: 
      # decompress the cube
      cube.fromNPZ ( row[0] )


  def getCubes ( self, listofidxs, resolution, dbname ):

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    # RBTODO need to fix this for neariso interfaces
    sql = "SELECT zindex, cube FROM " + dbname + " WHERE zindex IN (%s)" 

    # creats a %s for each list element
    in_p=', '.join(map(lambda x: '%s', listofidxs))
    # replace the single %s with the in_p string
    sql = sql % in_p

    try:
      rc = cursor.execute(sql, listofidxs)
    
      # Get the objects and add to the cube
      while ( True ):
        try: 
          retval = cursor.fetchone() 
        except:
          break
        if retval != None:
          yield ( retval )
        else:
          return
 
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()


  #
  # putCube
  #
  def putCube ( self, key, resolution, cube ):
    """Store a cube from the annotation database"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    # compress the cube
    npz = cube.toNPZ ()

    # we created a cube from zeros
    if cube.fromZeros ():

      sql = "INSERT INTO " + self.db.annoproj.getTable(resolution) +  "(zindex, cube) VALUES (%s, %s)"

      # this uses a cursor defined in the caller (locking context): not beautiful, but needed for locking
      try:
        cursor.execute ( sql, (key,npz))
      except MySQLdb.Error, e:
        logger.error ( "Error inserting cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise
      finally:
        # close the local cursor if not in a transaction
        # and commit right away
        if self.txncursor == None:
          cursor.close()

    else:

      sql = "UPDATE " + self.db.annoproj.getTable(resolution) + " SET cube=(%s) WHERE zindex=" + str(key)
      try:
        cursor.execute ( sql, (npz))
      except MySQLdb.Error, e:
        logger.error ( "Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise
      finally:
        # close the local cursor if not in a transaction
        # and commit right away
        if self.txncursor == None:
          cursor.close()

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()



  def getIndex ( self, entityid, resolution, update ):
    """MySQL fetch index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    #get the block from the database                                            
    sql = "SELECT cube FROM " + self.db.annoproj.getIdxTable(resolution) + " WHERE annid\
= " + str(entityid) 
    if update==True:
      sql += " FOR UPDATE"
    try:
      cursor.execute ( sql )
      row = cursor.fetchone ()
    except MySQLdb.Error, e:
      logger.warning ("Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    except BaseException, e:
      logger.exception("Unknown exception")
      raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()
   
    # If we can't find a index, they don't exist                                
    if ( row == None ):
       return []
    else:
       fobj = cStringIO.StringIO ( row[0] )
       return np.load ( fobj )      


  def putIndex ( self, key, index, resolution ):
    """MySQL put index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor


    sql = "INSERT INTO " +  self.db.annoproj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
    
    try:
       fileobj = cStringIO.StringIO ()
       np.save ( fileobj, index )
       cursor.execute ( sql, (key, fileobj.getvalue()))
    except MySQLdb.Error, e:
       logger.warning("Error updating index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except BaseException, e:
       logger.exception("Unknown error when updating index")
       raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()

  def updateIndex ( self, key, index, resolution ):
    """MySQL update index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    #update index in the database
    sql = "UPDATE " + self.db.annoproj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(key)
    try:
       fileobj = cStringIO.StringIO ()
       np.save ( fileobj, index )
       cursor.execute ( sql, (fileobj.getvalue()))
    except MySQLdb.Error, e:
       logger.warnig("Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except:
      logger.exception("Unknown exception")
      raise

    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()


  def deleteIndex ( self, annid, resolution ):
    """MySQL update index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    sql = "DELETE FROM " +  self.db.annoproj.getIdxTable(resolution)  +  " WHERE annid=" + str(annid)
    
    try:
       cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error("Error deleting the index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
       raise
    except:
      logger.exception("Unknown exception")
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()


  #
  # getExceptions
  #
  def getExceptions ( self, key, resolution, entityid ):
    """Load a the list of excpetions for this cube."""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    # get the block from the database
    sql = "SELECT exlist FROM %s where zindex=%s AND id=%s" % ( 'exc'+str(resolution), key, entityid )
    try:
      cursor.execute ( sql )
      row = cursor.fetchone()
    except MySQLdb.Error, e:
      logger.error ( "Error reading exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor == None:
        cursor.close()

    # If we can't find a list of exceptions, they don't exist
    if ( row == None ):
      return []
    else: 
      return np.load(cStringIO.StringIO ( zlib.decompress(row[0]) ))

  #
  # deleteExceptions
  #
  def deleteExceptions ( self, key, resolution, entityid ):
    """Delete a list of exceptions for this cuboid"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    table = 'exc'+str(resolution)

    sql = "DELETE FROM " + table + " WHERE zindex = %s AND id = %s" 
    try:
      self.txncursor.execute ( sql, (key, entityid))
    except MySQLdb.Error, e:
      logger.error ( "Error deleting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      if self.txncursor == None:
        cursor.close()
      raise

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()
      cursor.close()


  #
  # updateExceptions
  #
  def updateExceptions ( self, key, resolution, entityid, exceptions ):
    """Store a list of exceptions"""
    """This should be done in a transaction"""

    curexlist = self.getExceptions( key, resolution, entityid ) 

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    table = 'exc'+str(resolution)

    if curexlist==[]:

      sql = "INSERT INTO " + table + " (zindex, id, exlist) VALUES (%s, %s, %s)"
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, exceptions )
        cursor.execute ( sql, (key, entityid, zlib.compress(fileobj.getvalue())))
      except MySQLdb.Error, e:
        logger.error ( "Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        if self.txncursor == None:
          cursor.close()
        raise

    # In this case we have an update query
    else:

      oldexlist = [ zindex.XYZMorton ( trpl ) for trpl in curexlist ]
      newexlist = [ zindex.XYZMorton ( trpl ) for trpl in exceptions ]
      exlist = set(newexlist + oldexlist)
      exlist = [ zindex.MortonXYZ ( zidx ) for zidx in exlist ]

      sql = "UPDATE " + table + " SET exlist=(%s) WHERE zindex=%s AND id=%s" 
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, exlist )
        cursor.execute ( sql, (zlib.compress(fileobj.getvalue()),key,entityid))
      except MySQLdb.Error, e:
        logger.error ( "Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        if self.txncursor == None:
          cursor.close()
        raise

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()
      cursor.close()

  #
  # removeExceptions
  #
  def removeExceptions ( self, key, resolution, entityid, exceptions ):
    """Remove a list of exceptions"""
    """Should be done in a transaction"""

    curexlist = self.getExceptions( key, resolution, entityid ) 

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor == None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor


    table = 'exc'+str(resolution)

    if curexlist != []:

      oldexlist = set([ zindex.XYZMorton ( trpl ) for trpl in curexlist ])
      newexlist = set([ zindex.XYZMorton ( trpl ) for trpl in exceptions ])
      exlist = oldexlist-newexlist
      exlist = [ zindex.MortonXYZ ( zidx ) for zidx in exlist ]

      sql = "UPDATE " + table + " SET exlist=(%s) WHERE zindex=%s AND id=%s" 
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, exlist )
        self.txncursor.execute ( sql, (zlib.compress(fileobj.getvalue()),key,entityid))
      except MySQLdb.Error, e:
        logger.error("Error removing exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        if self.txncursor == None:
          cursor.close()
        raise

    # commit if not in a txn
    if self.txncursor == None:
      self.conn.commit()

