import numpy as np
import array
import cStringIO
import MySQLdb

import empaths
import dbconfig
import zindex
import emcaproj

import logging
logger=logging.getLogger("emca")

#
#  AnnotateIndex: Maintain the index in the database
# AUTHOR: Priya Manavalan

class AnnotateIndex:

  # Constructor 
  #
   def __init__(self,conn,proj):
      """Give an active connection.  This puts all index operations in the same transation as the calling db."""

      self.conn = conn
      self.proj = proj
   
   def __del__(self):
      """Destructor"""
      pass
   
   #
   # getIndex -- Retrieve the index for the annotation with id
   #
   def getIndex ( self, entityid, resolution ):

      #Establish a connection
      cursor = self.conn.cursor ()

      #get the block from the database                                            
      sql = "SELECT cube FROM " + self.proj.getIdxTable(resolution) + " WHERE annid\
 = " + str(entityid)
      try:
         cursor.execute ( sql )
      except MySQLdb.Error, e:
         logger.warning ("Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
         raise
      except BaseException, e:
         logger.exception("Unknown exception")
         raise
         
      row = cursor.fetchone ()
      cursor.close()
     
      # If we can't find a index, they don't exist                                
      if ( row == None ):
         return []
      else:
         fobj = cStringIO.StringIO ( row[0] )
         return np.load ( fobj )      

#
# Update Index Dense - Updated the annotation database with the given hash index table
#
   def updateIndexDense(self,index,resolution):
      """Updated the database index table with the input index hash table"""

      cursor = self.conn.cursor ()

      for key, value in index.iteritems():
         cubelist = list(value)
         cubeindex=np.array(cubelist)
         
         curindex = self.getIndex(key,resolution)
         
         if curindex==[]:
            sql = "INSERT INTO " +  self.proj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
            
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, cubeindex )
               cursor.execute ( sql, (key, fileobj.getvalue()))
            except MySQLdb.Error, e:
               logger.warning("Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
               raise
            except BaseException, e:
               logger.exception("Unknown error")
               raise
            
            # Almost certainly introduced this bug again.  Works on devel. machine.  Test on rio.
            #RBTODO why this commit for NPZ?  does it work without for RAmon
#            self.conn.commit()


         else:
             #Update index to the union of the currentIndex and the updated index
            newIndex=np.union1d(curindex,cubeindex)


            #update index in the database
            sql = "UPDATE " + self.proj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(key)
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, newIndex )
               cursor.execute ( sql, (fileobj.getvalue()))
            except MySQLdb.Error, e:
               logger.warnig("Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
               raise
            except:
              logger.exception("Unknown exception")
              raise

            #RBTODO why this commit for NPZ?  does it work without for RAmon
#            self.conn.commit()
               
      cursor.close()

   #
   #deleteIndex:
   #   Delete the index for a given annotation id
   #
   def deleteIndex(self,annid,resolutions):
      """delete the index for a given annid""" 
      
      cursor = self.conn.cursor ()

      #delete Index table for each resolution
      for res in resolutions:
         sql = "DELETE FROM " +  self.proj.getIdxTable(res)  +  " WHERE annid=" + str(annid)
         print sql
         
         try:
            cursor.execute ( sql )
         except MySQLdb.Error, e:
            logger.error("Error deleting the index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
            raise
         except:
           logger.exception("Unknown exception")
           raise

      cursor.close()
# end AnnotateIndex
