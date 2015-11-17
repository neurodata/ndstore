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
import re
from collections import defaultdict
import itertools
import blosc
from contextlib import closing
from operator import add, sub, div, mod
import MySQLdb

import ndlib
from ndtype import ANNOTATION_CHANNELS, TIMESERIES_CHANNELS, EXCEPTION_TRUE, PROPAGATED

import annotation

import logging
logger=logging.getLogger("neurodata")

"""
.. module:: ramonddb
    :synopsis: Manipulate/create/read annotations in the ramon format

.. moduleauthor:: Kunal Lillaney <lillaney@jhu.edu>
"""

class RamonDB:

  def __init__ (self, proj):
    """Connect with the brain databases"""

    self.datasetcfg = proj.datasetcfg
    self.proj = proj

    # Connection info for the metadata
    try:
      self.conn = MySQLdb.connect (host = self.proj.getDBHost(), user = self.proj.getDBUser(), passwd = self.proj.getDBPasswd(), db = self.proj.getDBName())
      # start with no cursor
      self.cursor = None
    except MySQLdb.Error, e:
      self.conn = None
      logger.error("Failed to connect to database: {}, {}".format(self.proj.getDBHost(), self.proj.getDBName()))

  def close ( self ):
    """Close the connection"""
    if self.conn:
      self.conn.close()

#
#  Cursor handling routines.  
#
  def getCursor ( self ):
    """If we are in a transaction, return the cursor, otherwise make one"""

    if self.cursor is None:
      return self.conn.cursor()
    else:
      return self.cursor

  def closeCursor ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor is None:
      cursor.close()

  def closeCursorCommit ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor is None:
      self.conn.commit()
      cursor.close()

  def commit ( self ):
    """Commit the transaction. Moved out of __del__ to make explicit.""" 

    if self.cursor is not None:
      self.cursor.close()
      self.conn.commit()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""

    if self.conn is not None:
      self.cursor = self.conn.cursor()
      sql = "START TRANSACTION"
      self.cursor.execute ( sql )

  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""

    if self.cursor is not None:
      self.cursor.close()
      self.conn.rollback()


  def peekID ( self ):
    """Look at the next ID but don't claim it.  This is an internal interface.
        It is not thread safe.  Need a way to lock the ids table for the 
        transaction to make it safe."""
    
    with closing(self.conn.cursor()) as cursor:

      # Query the current max identifier
      sql = "SELECT max(id) FROM " + str ( self.proj.getIdsTable() )
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.warning ("Problem retrieving identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
        raise

      # Here we've queried the highest id successfully    
      row = cursor.fetchone()
      # if the table is empty start at 1, 0 is no annotation
      if ( row[0] == None ):
        identifier = 1
      else:
        identifier = int ( row[0] ) + 1

      return identifier


  def nextID ( self, ch ):
    """Get an new identifier. This is it's own txn and should not be called inside another transaction."""

    with closing(self.conn.cursor()) as cursor:
    
      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format(ch.getIdsTable())
      try:

        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM {}".format(ch.getIdsTable()) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 1
        else:
          identifier = int ( row[0] ) + 1

        # increment and update query
        sql = "INSERT INTO {} VALUES ({})".format(ch.getIdsTable(), identifier)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier

  def setID ( self, ch, annoid ):
    """Set a user specified identifier in the ids table"""

    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format( ch.getIdsTable() )
      try:
        # try the insert, get ane exception if it doesn't work
        sql = "INSERT INTO {} VALUES({})".format(ch.getIdsTable(), annoid)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoid

  #
  #  setBatchID
  # 
  #  Place the user selected id into the ids table
  #
  def setBatchID ( self, annoidList ):
    """ Set a user specified identifier """

    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format(self.proj.getIdsTable())
      try:
        # try the insert, get and if it doesn't work
        sql = "INSERT INTO {} VALUES ( %s ) ".format( str(self.proj.getIdsTable()) )
        try:
          cursor.executemany ( sql, [str(i) for i in annoidList] )  
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoidList


  def reserve ( self, ch, count ):
    """Reserve contiguous identifiers. This is it's own txn and should not be called inside another transaction."""

    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format( ch.getIdsTable() )
      try:
        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM {}".format( ch.getIdsTable() ) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 0
        else:
          identifier = int ( row[0] ) 

        # increment and update query
        sql = "INSERT INTO {} VALUES ({}) ".format(ch.getIdsTable(), identifier+count)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      except Exception, e:
        logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier+1


  #
  # getAnnotation:
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, ch, annid ):
    """Return a RAMON object by identifier"""

    cursor = self.getCursor()
    try:
      return annotation.getAnnotation(ch, annid, self, cursor)
    except:
      self.closeCursor(cursor)
      raise

    self.closeCursorCommit(cursor)


  def updateAnnotation (self, ch, annid, field, value):
    """Update a RAMON object by identifier"""

    cursor = self.getCursor()
    try:
      anno = self.getAnnotation(ch, annid)
      if anno is None:
        logger.warning("No annotation found at identifier = {}".format(annid))
        raise OCPCAError ("No annotation found at identifier = {}".format(annid))
      anno.setField(field, value)
      anno.update(ch, cursor)
    except:
      self.closeCursor(cursor)
      raise
    self.closeCursorCommit(cursor)


  def putAnnotation ( self, ch, anno, options='' ):
    """store an HDF5 annotation to the database"""

    cursor = self.getCursor()
    try:
      retval = annotation.putAnnotation(ch, anno, self, cursor, options)
    except:
      self.closeCursor(cursor)
      raise

    self.closeCursorCommit(cursor)

    return retval


  def deleteAnnotation ( self, ch, annoid, options='' ):
    """delete an HDF5 annotation from the database"""

    cursor = self.getCursor()
    try:
      retval = annotation.deleteAnnotation ( ch, annoid, self, cursor, options )
    except:
      self.closeCursor( cursor )
      raise

    self.closeCursorCommit(cursor)

    return retval

  def getChildren ( self, ch, annoid ):
    """get all the children of the annotation"""

    cursor = self.getCursor()
    try:
      retval = annotation.getChildren (ch, annoid, self, cursor)
    finally:
      self.closeCursor ( cursor )

    return retval


  # getAnnoObjects:
  #    Return a list of annotation object IDs
  #  for now by type and status
  def getAnnoObjects ( self, ch, args ):
    """Return a list of annotation object ids that match equality predicates.
      Legal predicates are currently:
        type
        status
      Predicates are given in a dictionary.
    """

    # legal equality fields
    eqfields = ( 'type', 'status' )
    # legal comparative fields
    compfields = ( 'confidence' )

    # start of the SQL clause
    sql = "SELECT annoid FROM {}".format(ch.getAnnoTable('annotation'))
    clause = ''
    limitclause = ""

    # iterate over the predicates
    it = iter(args)
    try:

      field = it.next()

      # build a query for all the predicates
      while ( field ):

        # provide a limit clause for iterating through the database
        if field == "limit":
          val = it.next()
          if not re.match('^\d+$',val):
            logger.warning ( "Limit needs an integer. Illegal value:%s" % (field,val) )
            raise OCPCAError ( "Limit needs an integer. Illegal value:%s" % (field,val) )

          limitclause = " LIMIT %s " % (val)

        # all other clauses
        else:
          if clause == '':
            clause += " WHERE "
          else:
            clause += ' AND '

          if field in eqfields:
            val = it.next()
            if not re.match('^\w+$',val):
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )

            clause += '%s = %s' % ( field, val )

          elif field in compfields:

            opstr = it.next()
            if opstr == 'lt':
              op = ' < '
            elif opstr == 'gt':
              op = ' > '
            else:
              logger.warning ( "Not a comparison operator: %s" % (opstr) )
              raise OCPCAError ( "Not a comparison operator: %s" % (opstr) )

            val = it.next()
            if not re.match('^[\d\.]+$',val):
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )
            clause += '%s %s %s' % ( field, op, val )


          #RB TODO key/value fields?

          else:
            raise OCPCAError ( "Illegal field in URL: %s" % (field) )

        field = it.next()

    except StopIteration:
      pass

    sql += clause + limitclause + ';'

    cursor = self.getCursor()

    try:
      cursor.execute ( sql )
      annoids = np.array ( cursor.fetchall(), dtype=np.uint32 ).flatten()
    except MySQLdb.Error, e:
      logger.error ( "Error retrieving ids: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor( cursor )

    return np.array(annoids)




