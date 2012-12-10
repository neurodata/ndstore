import empaths
import MySQLdb
import h5py
import numpy as np

import emcaprivate
from emcaerror import ANNError
import dbconfig

#TODO enforce readonly

# dbtype enumerations
IMAGES = 1
ANNOTATIONS = 2
CHANNELS = 3

class EMCAProject:
  """Project specific for cutout and annotation data"""

  # Constructor 
  def __init__(self, dbname, dbhost, dbtype, dataset, dataurl, resolution, readonly, exceptions ):
    """Initialize the EMCA Project"""
    
    self._dbname = dbname
    self._dbhost = dbhost
    self._dbtype = dbtype
    self._dataset = dataset
    self._dataurl = dataurl
    self._resolution = resolution
    self._readonly = readonly
    self._exceptions = exceptions
    self._dbtype = dbtype

    # Could add these to dbconfig.  Probably remove res as tablebase instead
    self._ids_tbl = "ids"

  # Accessors
  def getDBHost ( self ):
    return self._dbhost
  def getDBType ( self ):
    return self._dbtype
  def getDBName ( self ):
    return self._dbname
  def getDataset ( self ):
    return self._dataset
  def getDataURL ( self ):
    return self._dataurl
  def getResolution ( self ):
    return self._resolution
  def getIDsTbl ( self ):
    return self._ids_tbl
  def getExceptions ( self ):
    return self._exceptions
  def getDBType ( self ):
    return self._dbtype
    

  # accessors for RB to fix
  def getDBUser( self ):
    return emcaprivate.dbuser
  def getDBPasswd( self ):
    return emcaprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx"+str(resolution)

  def h5Info ( self, h5f ):
    """Populate the HDF5 file with project attributes"""

    projgrp = h5f.create_group ( 'PROJECT' )
    projgrp.create_dataset ( "NAME", (1,), dtype=h5py.special_dtype(vlen=str), data=self._dbname )
    projgrp.create_dataset ( "HOST", (1,), dtype=h5py.special_dtype(vlen=str), data=self._dbhost )
    projgrp.create_dataset ( "TYPE", (1,), dtype=np.uint32, data=self._dbtype )
    projgrp.create_dataset ( "DATASET", (1,), dtype=h5py.special_dtype(vlen=str), data=self._dataset )
    projgrp.create_dataset ( "DATAURL", (1,), dtype=h5py.special_dtype(vlen=str), data=self._dataurl )
    projgrp.create_dataset ( "RESOLUTION", (1,), dtype=np.uint32, data=self._resolution )
    projgrp.create_dataset ( "READONLY", (1,), dtype=bool, data=(False if self._readonly==0 else True))
    projgrp.create_dataset ( "EXCEPTIONS", (1,), dtype=bool, data=(False if self._exceptions==0 else True))

class EMCAProjectsDB:
  """Database for the annotation and cutout projects"""

  def openConn (self):
    """Create the database connection"""

    # Connection info in dbconfig
    try:
      self.conn = MySQLdb.connect (host = emcaprivate.dbhost,
                          user = emcaprivate.dbuser,
                          passwd = emcaprivate.dbpasswd,
                          db = emcaprivate.db )
    except:
      self.conn = None
      raise ANNError ( "Failed to connect to host/table", emcaprivate.dbhost, emcaprivate.db ) 
                          

  def closeConn (self):
    """Close the database connection"""
    if self.conn:
      self.conn.close()

  #
  # Load the emca databse information based on the token
  #
  def getProj ( self, token ):
    """Load the annotation database information based on the token"""


    # Lookup the information for the database project based on the token
    sql = "SELECT * from %s where token = \'%s\'" % (emcaprivate.table, token)

    try:
      self.openConn()
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Could not query emca projects database"
      raise ANNError ( "EMCA Project Database error" )

    # get the project information 
    row = cursor.fetchone()

    self.closeConn()

    # if the project is not found.  error
    if ( row == None ):
      print "No project found"
      raise ANNError ( "Project token not found" )

    [token, openid, host, project, dbtype, dataset, dataurl, resolution, readonly, exceptions ] = row

    return EMCAProject ( project, host, dbtype, dataset, dataurl, resolution, readonly, exceptions )


  #
  # Load the  database information based on the token
  #
  def newEMCAProj ( self, token, openid, dbhost, project, dbtype, dataset, dataurl, resolution, readonly, exceptions ):
    """Create a new emca project"""

# TODO need to undo the project creation if not totally sucessful

    dbcfg = dbconfig.switchDataset ( dataset )

    print dbhost, project

    # Insert the project entry into the database
    sql = "INSERT INTO {0} VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},\'{6}\',\'{7}\',{8},{9},{10})".format (\
        emcaprivate.table, token, openid, dbhost, project, dbtype, dataset, dataurl, resolution, readonly, exceptions )

    print sql

   
    try:
      self.openConn()
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create new project", e
      raise ANNError ( "Failed to create new project" )


    self.conn.commit()
    self.closeConn()

    # Connect to the new database
    newconn = MySQLdb.connect (host = dbhost,
                          user = emcaprivate.dbuser,
                          passwd = emcaprivate.dbpasswd )

    newcursor = newconn.cursor()
  

    # Make the database and associated emca tables
    sql = "CREATE DATABASE %s;" % project
    print "Executing: ", sql
   
    try:
      newcursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create database for new project", e
      raise ANNError ( "Failed to create database for new project" )

    newconn.commit()
    newconn.close()

    # Connect to the new database
    newconn = MySQLdb.connect (host = dbhost,
                          user = emcaprivate.dbuser,
                          passwd = emcaprivate.dbpasswd,
                          db = project )

    newcursor = newconn.cursor()

    sql = ""

    # tables for annotations and images
    if dbtype == IMAGES or dbtype == ANNOTATIONS:

      for i in dbcfg.resolutions: 
        sql += "CREATE TABLE res%s ( zindex BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i

    # tables for channel dbs
    if dbtype == CHANNELS:
      for i in dbcfg.resolutions: 
        sql += "CREATE TABLE res%s ( zindex BIGINT, channel INT, cube LONGBLOB, PRIMARY KEY(zindex,channel) );\n" % i

    # tables specific to annotation projects
    if dbtype == ANNOTATIONS:

      sql += "CREATE TABLE ids ( id BIGINT PRIMARY KEY);\n"

      # And the RAMON objects
      sql += "CREATE TABLE annotations (annoid BIGINT PRIMARY KEY, type INT, confidence FLOAT, status INT);\n"
      sql += "CREATE TABLE seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT);\n"
      sql += "CREATE TABLE synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT);\n"
      sql += "CREATE TABLE segments (annoid BIGINT PRIMARY KEY, segmentclass INT, parentseed INT, neuron INT);\n"
      sql += "CREATE TABLE organelles (annoid BIGINT PRIMARY KEY, organelleclass INT, parentseed INT, centroidx INT, centroidy INT, centroidz INT);\n"
      sql += "CREATE TABLE kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(64000), PRIMARY KEY ( annoid, kv_key ));\n"

      for i in dbcfg.resolutions: 
        if exceptions:
          sql += "CREATE TABLE exc%s ( zindex BIGINT, id INT, exlist LONGBLOB, PRIMARY KEY ( zindex, id));\n" % i
        sql += "CREATE TABLE idx%s ( annid BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i

    print sql

    try:
      cursor = newconn.cursor()
      newcursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create tables for new project", e
      raise ANNError ( "Failed to create database for new project" )

    newconn.commit()
    newconn.close()


  def deleteEMCAProj ( self, token ):
    """Create a new emca project"""

    proj = self.getProj ( token )
    sql = "DELETE FROM %s WHERE token=\'%s\'" % ( emcaprivate.table, token ) 

    print sql
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      raise ANNError ( "Failed to remove project from projects table" )

    self.conn.commit()

  def deleteEMCADB ( self, token ):

    # load the project
    proj = self.getProj ( token )

    # delete line from projects table
    self.deleteEMCAProj ( token )

    # delete the database
    sql = "DROP DATABASE " + proj.getDBName()

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      raise ANNError ( "Failed to remove project from projects table" )

    self.conn.commit()




    

  # accessors for RB to fix
  def getDBUser( self ):
    return emcaprivate.dbuser
  def getDBPasswd( self ):
    return emcaprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx"+str(resolution)

