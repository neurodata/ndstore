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
   # getIndex -- Retrieve the index for the annotation with id
   #
   def getIndex ( self, entityid, resolution ):
    #Establish a connection
      cursor = self.conn.cursor ()

  # PYTODO rename cube to cubes
     
    #get the block from the database                                            
      sql = "SELECT cube FROM " + self.annoproj.getIdxTable(resolution) + " WHERE annid\
 = " + str(entityid)
      #print sql
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
# Update Index Dense - Updated the annotation database with the given hash index table
#
   def updateIndexDense(self,index,resolution):
      """Updated the database index table with the input index hash table"""
      for key, value in index.iteritems():
         cubelist = list(value)
         cubeindex=np.array(cubelist)
         #print cubeindex
         
         cursor = self.conn.cursor ()
         curindex = self.getIndex(key,resolution)
         
    #Used for testing
         #print ("Current Index", curindex )
         if curindex==[]:
            print "Adding a new Index for annotation", key, ": ", cubeindex
            sql = "INSERT INTO " +  self.annoproj.getIdxTable(resolution)  +  "( annid, cube) VALUES ( %s, %s)"
            
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, cubeindex )
          #     print sql, key
               cursor.execute ( sql, (key, fileobj.getvalue()))
            except MySQLdb.Error, e:
               print "Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
               assert 0
            except BaseException, e:
               print "DBG: SOMETHING REALLY WRONG HERE", e
         else:
             #Update index to the union of the currentIndex and the updated index                                                               
            newIndex=np.union1d(curindex,cubeindex)
            print "Updating Index for annotation ",key, " to" , newIndex
            
         #update index in the database                                                                                                      
            sql = "UPDATE " + self.annoproj.getIdxTable(resolution) + " SET cube=(%s) WHERE annid=" + str(key)
            try:
               fileobj = cStringIO.StringIO ()
               np.save ( fileobj, newIndex )
               cursor.execute ( sql, (fileobj.getvalue()))
            except MySQLdb.Error, e:
               print "Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
               assert 0
               
      cursor.close()
      self.conn.commit()
              #self.updateIndex(key,cubeIdx,resolution)
      pass



# end AnnotateIndex
