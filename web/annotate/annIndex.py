import numpy as np
import array
import cStringIO
#from PIL import Image
#import zlib
import MySQLdb

import empaths
import dbconfig
import zindex
import annproj
#from ann_cy import annotate_cy


#
#  AnnotateIndex: Maintain the index in the database
# AUTHOR: Priya Manavalan

class AnnotateIndex:

  # Constructor 
  #
   def __init__(self,dbconf,annoproj):
      print "in Annotate Index"
      self.dbcfg = dbconf
      self.annoproj = annoproj
      
      dbinfo = self.annoproj.getDBHost(), self.annoproj.getDBUser(), self.annoproj.getDBPasswd(), self.annoproj.getDBName()

    # Connection info                                                                                                
      try:
         self.conn = MySQLdb.connect (host = self.annoproj.getDBHost(),
                                      user = self.annoproj.getDBUser(),
                                      passwd = self.annoproj.getDBPasswd(),
                                      db = self.annoproj.getDBName())
      except:
         raise AnnError ( dbinfo )
    
    # How many slices?                                                                                               
      [ self.startslice, endslice ] = self.dbcfg.slicerange
      self.slices = endslice - self.startslice + 1
      pass
   
   def __del__(self):
      """Destructor"""
      pass
   
   #
   # updateIndex -- Update the index of the annotation with id in the database
   # entityId - annotation id
   # cubeIdx - array of cubelocations                                                                                 
   # 
   def updateIndex ( self, entityid,cubeIdx,resolution ):
      print "in update Index with annotation is :", entityid
      cursor = self.conn.cursor ()
      #Check if index already exists for a given annotation id                    
      curIndex = self.getIndex(entityid,resolution)
      
    #Used for testing                                                           
      print ("Current Index", curIndex )
      if curIndex==[]:
         print "Adding a new Index for annotation", entityid, ": ", cubeIdx
         sql = "INSERT INTO " +  self.annoproj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
         
         try:
            fileobj = cStringIO.StringIO ()
            np.save ( fileobj, cubeIdx )
            print sql, entityid
            cursor.execute ( sql, (entityid, fileobj.getvalue()))
         except MySQLdb.Error, e:
            print "Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
            assert 0
         except BaseException, e:
            print "DBG: SOMETHING REALLY WRONG HERE", e
      else:
         #Update index to the union of the currentIndex and the updated index
         newIndex=np.union1d(curIndex,cubeIdx)
         print "Updating Index for annotation ",entityid, " to" , newIndex
         
         #update index in the database
         sql = "UPDATE " + self.annoproj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(entityid)
         try:
            fileobj = cStringIO.StringIO ()
            np.save ( fileobj, newIndex )
            cursor.execute ( sql, (fileobj.getvalue()))
         except MySQLdb.Error, e:
            print "Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
            assert 0

      cursor.close()
      self.conn.commit()
      
      pass

   #
   # getIndex -- Retrieve the index for the annotation with id
   #
   def getIndex ( self, entityid,resolution ):
    #Establish a connection
      print "In getIndex with id!", entityid                                      
      cursor = self.conn.cursor ()
     
    #get the block from the database                                            
      sql = "SELECT cube FROM " + self.annoproj.getIdxTable(resolution) + " WHERE annid\
 = " + str(entityid)
      print sql
      try:
         cursor.execute ( sql )
      except MySQLdb.Error, e:
         print "Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
         assert 0
      except BaseException, e:
         print "DBG: SOMETHING REALLY WRONG HERE", e
         
      row = cursor.fetchone ()
      cursor.close()
     
    # If we can't find a index, they don't exist                                
      if ( row == None ):
         return []
      else:
         fobj = cStringIO.StringIO ( row[0] )
         return np.load ( fobj )      
#   
#saveIndex - Stores an index for an annotation to the database
# Used when building an index for an existing database
#
   def saveIndex(self,key,value,resolution):
      #print "Saving Index for annotaton ",key, " which has cubenuumbers " , value
      
      # compress the index and write it to the database
      cubeIdx = np.array(value)
      self.updateIndex(key,cubeIdx,resolution)
      pass
# end AnnotateIndex
