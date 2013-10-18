import numpy as np
import array
import cStringIO
import MySQLdb

import zindex
import ocpcaproj

import logging
logger=logging.getLogger("ocp")

#
#  AnnotateIndex: Maintain the index in the database
# AUTHOR: Priya Manavalan

class AnnotateIndex:

  # Constructor 
  #
   def __init__(self,conn,cursor,proj):
      """Give an active connection.  This puts all index operations in the same transation as the calling db."""

      self.conn = conn
      self.proj = proj
      self.cursor = cursor
   
   def __del__(self):
      """Destructor"""
   
   #
   # getIndex -- Retrieve the index for the annotation with id
   #
   def getIndex ( self, entityid, resolution, update=False ):

      #get the block from the database                                            
      sql = "SELECT cube FROM " + self.proj.getIdxTable(resolution) + " WHERE annid\
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

#
# Update Index Dense - Updated the annotation database with the given hash index table
#
   def updateIndexDense(self,index,resolution):
      """Updated the database index table with the input index hash table"""

      for key, value in index.iteritems():
         cubelist = list(value)
         cubeindex=np.array(cubelist)
         
         curindex = self.getIndex(key,resolution,True)
         
         if curindex==[]:
            sql = "INSERT INTO " +  self.proj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
            
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, cubeindex )
               self.cursor.execute ( sql, (key, fileobj.getvalue()))
            except MySQLdb.Error, e:
               logger.warning("Error updating index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
               raise
            except BaseException, e:
               logger.exception("Unknown error when updating index")
               raise
            
         else:
             #Update index to the union of the currentIndex and the updated index
            newIndex=np.union1d(curindex,cubeindex)


            #update index in the database
            sql = "UPDATE " + self.proj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(key)
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, newIndex )
               self.cursor.execute ( sql, (fileobj.getvalue()))
            except MySQLdb.Error, e:
               logger.warnig("Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
               raise
            except:
              logger.exception("Unknown exception")
              raise

   #
   #deleteIndex:
   #   Delete the index for a given annotation id
   #
   def deleteIndex(self,annid,resolutions):
      """delete the index for a given annid""" 
      
      #delete Index table for each resolution
      for res in resolutions:
         sql = "DELETE FROM " +  self.proj.getIdxTable(res)  +  " WHERE annid=" + str(annid)
         
         try:
            self.cursor.execute ( sql )
         except MySQLdb.Error, e:
            logger.error("Error deleting the index %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
            raise
         except:
           logger.exception("Unknown exception")
           raise

# end AnnotateIndex
