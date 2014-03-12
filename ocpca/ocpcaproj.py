import MySQLdb
import h5py
import numpy as np
import math

import ocpcaprivate
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

# dbtype enumerations
IMAGES_8bit = 1
ANNOTATIONS = 2
CHANNELS_16bit = 3
CHANNELS_8bit = 4
PROBMAP_32bit = 5
BITMASK = 6
ANNOTATIONS_64bit = 7 

class OCPCAProject:
  """Project specific for cutout and annotation data"""

  # Constructor 
  def __init__(self, dbname, dbhost, dbtype, dataset, dataurl, readonly, exceptions, resolution ):
    """Initialize the OCPCA Project"""
    
    self._dbname = dbname
    self._dbhost = dbhost
    self._dbtype = dbtype
    self._dataset = dataset
    self._dataurl = dataurl
    self._readonly = readonly
    self._exceptions = exceptions
    self._resolution = resolution

    # Could add these to configuration.  Probably remove res as tablebase instead
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
  def getIDsTbl ( self ):
    return self._ids_tbl
  def getExceptions ( self ):
    return self._exceptions
  def getDBType ( self ):
    return self._dbtype
  def getReadOnly ( self ):
    return self._readonly
  def getResolution ( self ):
    return self._resolution

  # accessors for RB to fix
  def getDBUser( self ):
    return ocpcaprivate.dbuser
  def getDBPasswd( self ):
    return ocpcaprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)

  def getIsotropicTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)+"iso"

  def getNearIsoTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)+"neariso"
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx"+str(resolution)

class OCPCADataset:
  """Configuration for a dataset"""

  def __init__ ( self, ximagesz, yimagesz, startslice, endslice, zoomlevels, zscale ):
    """Construct a db configuration from the dataset parameters""" 

    self.slicerange = [ startslice, endslice ]

    # istropic slice range is a function of resolution
    self.isoslicerange = {} 
    self.nearisoscaledown = {}

    self.resolutions = []
    self.cubedim = {}
    self.imagesz = {}
    self.zscale = {}

    for i in range (zoomlevels+1):
      """Populate the dictionaries"""

      # add this level to the resolutions
      self.resolutions.append( i )

      # set the zscale factor
      self.zscale[i] = float(zscale)/(2**i);

      # choose the cubedim as a function of the zscale
      #  this may need to be changed.  
      if self.zscale[i] >  0.5:
        self.cubedim[i] = [128, 128, 16]
      else: 
        self.cubedim[i] = [64, 64, 64]

      # Make an exception for bock11 data -- just an inconsistency in original ingest
      if ximagesz == 135424 and i == 5:
        self.cubedim[i] = [128, 128, 16]

      # set the image size
      #  the scaled down image rounded up to the nearest cube
      xpixels=((ximagesz-1)/2**i)+1
      ximgsz = (((xpixels-1)/self.cubedim[i][0])+1)*self.cubedim[i][0]
      ypixels=((yimagesz-1)/2**i)+1
      yimgsz = (((ypixels-1)/self.cubedim[i][1])+1)*self.cubedim[i][1]
      self.imagesz[i] = [ ximgsz, yimgsz ]

      # set the isotropic image size when well defined
      if self.zscale[i] < 1.0:
        self.isoslicerange[i] = [ startslice, startslice + int(math.floor((endslice-startslice+1)*self.zscale[i])) ]

        # find the neareat to isotropic value
        scalepixels = 1/self.zscale[i]
        if ((math.ceil(scalepixels)-scalepixels)/scalepixels) <= ((scalepixels-math.floor(scalepixels))/scalepixels):
          self.nearisoscaledown[i] = int(math.ceil(scalepixels))
        else:
          self.nearisoscaledown[i] = int(math.floor(scalepixels))

      else:
        self.isoslicerange[i] = self.slicerange
        self.nearisoscaledown[i] = int(1)

  #
  #  Check that the specified arguments are legal
  #
  def checkCube ( self, resolution, xstart, xend, ystart, yend, zstart, zend ):
    """Return true if the specified range of values is inside the cube"""

    [xmax, ymax] = self.imagesz [ resolution ]

    if (( xstart >= 0 ) and ( xstart < xend) and ( xend <= self.imagesz[resolution][0]) and\
        ( ystart >= 0 ) and ( ystart < yend) and ( yend <= self.imagesz[resolution][1]) and\
        ( zstart >= self.slicerange[0] ) and ( zstart < zend) and ( zend <= (self.slicerange[1]+1))):
      return True
    else:
      return False

#
  #  Return the image size
  #
  def imageSize ( self, resolution ):
    return  [ self.imagesz [resolution], self.slicerange ]


class OCPCAProjectsDB:
  """Database for the annotation and cutout projects"""

  def __init__(self):
    """Create the database connection"""

    # Connection info 
    self.conn = MySQLdb.connect (host = ocpcaprivate.dbhost,
                          user = ocpcaprivate.dbuser,
                          passwd = ocpcaprivate.dbpasswd,
                          db = ocpcaprivate.db )

  #
  # Load the ocpca databse information based on the token
  #
  def loadProject ( self, token ):
    """Load the annotation database information based on the token"""

    # Lookup the information for the database project based on the token
    sql = "SELECT token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions, resolution from %s where token = \'%s\'" % (ocpcaprivate.projects, token)

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # get the project information 
    row= cursor.fetchone()

    # if the project is not found.  error
    if ( row == None ):
      logger.warning ( "Project token %s not found." % ( token ))
      raise OCPCAError ( "Project token %s not found." % ( token ))

    [token, openid, host, project, dbtype, dataset, dataurl, readonly, exceptions, resolution ] = row

    # Create a project object
    proj = OCPCAProject ( project, host, dbtype, dataset, dataurl, readonly, exceptions, resolution ) 
    proj.datasetcfg = self.loadDatasetConfig ( dataset )

    return proj

  #
  # Create a new dataset
  #
  def newDataset ( self, dsname, ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale ):
    """Create a new ocpca dataset"""

    sql = "INSERT INTO {0} (dataset, ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},\'{6}\',\'{7}\')".format (\
       ocpcaprivate.datasets, dsname, ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale )

    logger.info ( "Creating new dataset. Name %s. SQL=%s" % ( dsname, sql ))

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("Could not query ocpca datsets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Could not query ocpca datsets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    self.conn.commit()


  #
  # Create a new project (annotation or data)
  #
  def newOCPCAProj ( self, token, openid, dbhost, project, dbtype, dataset, dataurl, readonly, exceptions, nocreate, resolution ):
    """Create a new ocpca project"""

# TODO need to undo the project creation if not totally sucessful
    datasetcfg = self.loadDatasetConfig ( dataset )

    sql = "INSERT INTO {0} (token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions, resolution) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\')".format (\
       ocpcaprivate.projects, token, openid, dbhost, project, dbtype, dataset, dataurl, int(readonly), int(exceptions), resolution )

    logger.info ( "Creating new project. Host %s. Project %s. SQL=%s" % ( dbhost, project, sql ))

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    self.conn.commit()

    # Exception block around database creation
    try:

      # Make the database unless specified
      if not nocreate: 
       
        # Connect to the new database
        newconn = MySQLdb.connect (host = dbhost,
                              user = ocpcaprivate.dbuser,
                              passwd = ocpcaprivate.dbpasswd )

        newcursor = newconn.cursor()
      

        # Make the database and associated ocpca tables
        sql = "CREATE DATABASE %s;" % project
       
        try:
          newcursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise OCPCAError ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

        newconn.commit()

        # Connect to the new database
        newconn = MySQLdb.connect (host = dbhost,
                              user = ocpcaprivate.dbuser,
                              passwd = ocpcaprivate.dbpasswd,
                              db = project )

        newcursor = newconn.cursor()

        sql = ""

        # tables for annotations and images
        if dbtype==IMAGES_8bit or dbtype==ANNOTATIONS or dbtype==PROBMAP_32bit or dbtype==BITMASK:

          for i in datasetcfg.resolutions: 
            sql += "CREATE TABLE res%s ( zindex BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i

        # tables for channel dbs
        if dbtype == CHANNELS_8bit or dbtype == CHANNELS_16bit:
          sql += 'CREATE TABLE channels ( chanstr VARCHAR(255), chanid INT, PRIMARY KEY(chanstr));\n'
          for i in datasetcfg.resolutions: 
            sql += "CREATE TABLE res%s ( channel INT, zindex BIGINT, cube LONGBLOB, PRIMARY KEY(channel,zindex) );\n" % i

        # tables specific to annotation projects
        if dbtype == ANNOTATIONS or dbtype ==ANNOTATIONS_64bit:

          sql += "CREATE TABLE ids ( id BIGINT PRIMARY KEY);\n"

          # And the RAMON objects
          sql += "CREATE TABLE annotations (annoid BIGINT PRIMARY KEY, type INT, confidence FLOAT, status INT);\n"
          sql += "CREATE TABLE seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT);\n"
          sql += "CREATE TABLE synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT);\n"
          sql += "CREATE TABLE segments (annoid BIGINT PRIMARY KEY, segmentclass INT, parentseed INT, neuron INT);\n"
          sql += "CREATE TABLE organelles (annoid BIGINT PRIMARY KEY, organelleclass INT, parentseed INT, centroidx INT, centroidy INT, centroidz INT);\n"
          sql += "CREATE TABLE kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ));\n"

          for i in datasetcfg.resolutions: 
            if exceptions:
              sql += "CREATE TABLE exc%s ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id));\n" % i
            sql += "CREATE TABLE idx%s ( annid BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i

        try:
          cursor = newconn.cursor()
          newcursor.execute ( sql )
        except MySQLdb.Error, e:
          logging.error ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise OCPCAError ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Error, undo the projects table entry
    except:
      sql = "DELETE FROM {0} WHERE token=\'{1}\'".format (ocpcaprivate.projects, token)

      logger.info ( "Could not create project database.  Undoing projects insert. Project %s. SQL=%s" % ( project, sql ))

      try:
        cursor = self.conn.cursor()
        cursor.execute ( sql )
        self.conn.commit()
      except MySQLdb.Error, e:
        logger.error ("Could not undo insert into ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        logger.error ("Check project database for project not linked to database.")
        raise

    

  def deleteOCPCAProj ( self, token ):
    """Create a new ocpca project"""

    proj = self.loadProject ( token )
    sql = "DELETE FROM %s WHERE token=\'%s\'" % ( ocpcaprivate.projects, token ) 

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      logging.error ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    self.conn.commit()


  def deleteOCPCADB ( self, token ):

    # load the project
    proj = self.loadProject ( token )

    # delete line from projects table
    self.deleteOCPCAProj ( token )

    # delete the database
    sql = "DROP DATABASE " + proj.getDBName()

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      logging.error ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    self.conn.commit()

  # accessors for RB to fix
  def getDBUser( self ):
    return ocpcaprivate.dbuser
  def getDBPasswd( self ):
    return ocpcaprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx"+str(resolution)

  def loadDatasetConfig ( self, dataset ):
    """Query the database for the dataset information and build a db configuration"""
    sql = "SELECT ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale from %s where dataset = \'%s\'" % (ocpcaprivate.datasets, dataset)

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:

      logger.error ("Could not query ocpca datasets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Could not query ocpca datasets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # get the project information 
    row = cursor.fetchone()

    # if the project is not found.  error
    if ( row == None ):
      logger.warning ( "Dataset %s not found." % ( dataset ))
      raise OCPCAError ( "Dataset %s not found." % ( dataset ))

    [ ximagesz, yimagesz, startslice, endslice, zoomlevels, zscale ] = row
    return OCPCADataset ( int(ximagesz), int(yimagesz), int(startslice), int(endslice), int(zoomlevels), float(zscale) ) 


  #
  # Load the ocpca databse information based on openid
  #
  def getFilteredProjects ( self, openid, filterby, filtervalue ):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    #url = "SELECT * from %s where " + filterby
    #sql = "SELECT * from %s where %s = \'%s\'" % (ocpcaprivate.table, filterby, filtervalue)
    token_desc = ocpcaprivate.token_description;
    proj_tbl = ocpcaprivate.projects;
    if (filterby == ""):
      sql = "SELECT * from %s LEFT JOIN %s on %s.token = %s.token where %s.openid = \'%s\' ORDER BY project" % (ocpcaprivate.projects,token_desc,proj_tbl,token_desc,proj_tbl,openid)
    else:
      sql = "SELECT * from %s LEFT JOIN %s on %s.token = %s.token where %s.openid = \'%s\' and %s.%s = \'%s\' ORDER BY project" % (ocpcaprivate.projects,token_desc,proj_tbl,token_desc, proj_tbl,openid, proj_tbl,filterby, filtervalue.strip())
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error ("FAILED TO FILTER")
       raise
    # get the project information
   
    row = cursor.fetchall()
    return row

#*******************************************************************************
  #
  # Load the ocpca databse information based on openid and filter options
  #
  def getFilteredProjs ( self, openid, filterby, filtervalue,dataset ):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    proj_desc = ocpcaprivate.project_description;
    proj_tbl = ocpcaprivate.projects;
    if (filterby == ""):
      sql = "SELECT * from %s LEFT JOIN %s on %s.project = %s.project where %s.openid = \'%s\' and %s.dataset = \'%s\'" % (ocpcaprivate.projects,proj_desc,proj_tbl,proj_desc,proj_tbl,openid,proj_tbl,dataset)
    else:
      sql = "SELECT * from %s LEFT JOIN %s on %s.project = %s.project where %s.openid = \'%s\' and %s.%s = \'%s\' and %s.dataset =\'%s\'" % (ocpcaprivate.projects,proj_desc,proj_tbl,proj_desc, proj_tbl,openid, proj_tbl,filterby, filtervalue.strip(),proj_tbl,dataset)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error ("FAILED TO FILTER")
       raise
    # get the project information

    row = cursor.fetchall()
    return row

  #
  # Load Projects created by user ( projadmin)
  #
  def getDatabases ( self, openid):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    
    token_desc = ocpcaprivate.token_description;
    proj_tbl = ocpcaprivate.projects;

    sql = "SELECT distinct(dataset) from %s where openid = \'%s\'"  % (ocpcaprivate.projects,openid)
       
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error ("FAILED TO FILTER")
       raise
    # get the project information

    row = cursor.fetchall()
    return row

  #
  # Load Projects created by user ( projadmin)
  #
  def getDatasets ( self):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    sql = "SELECT * from %s"  % (ocpcaprivate.datasets)

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error ("FAILED TO FILTER")
       raise
    # get the project information

    row = cursor.fetchall()
    return row

   
#******************************************************************************

  #
  # Update the token for a project
  #
  def updateProject ( self, curtoken ,newtoken):
    """Load the annotation database information based on the openid"""
    sql = "UPDATE %s SET token = \'%s\' where token = \'%s\'" % (ocpcaprivate.projects, newtoken, curtoken)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
       logger.error ("FAILED TO UPDATE")
       raise
    # get the project information                                                                                                          
    self.conn.commit()

    #
    # Add token descriptiton for new projects
    #
  def insertTokenDescription ( self, token ,desc):
    """Add a token description for a new project"""
   # sql = "UPDATE %s SET token = \'%s\' where token = \'%s\'" % (ocpcaprivate.projects, newtoken, curtoken)
    sql = "INSERT INTO %s (token,description) VALUES (\'%s\',\'%s\')" % (ocpcaprivate.token_description, token, desc)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("FAILED TO INSERT NEW TOKEN DESCRIPTION")
      raise
    # get the project information
    self.conn.commit()

    #
    # Update token descriptiton a project
    #
  def updateTokenDescription ( self, token ,description):
    """Update token description for a project"""
    sql = "UPDATE %s SET description = \'%s\' where token = \'%s\'" % (ocpcaprivate.token_description, description, token)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("FAILED TO UPDATE TOKEN DESCRIPTION")
      raise
    self.conn.commit()

    #
    # Delete row from token_description table
    # Used with delete project
    #
  def deleteTokenDescription ( self, token):
    """Delete entry from token description table"""
    sql = "DELETE FROM  %s where token = \'%s\'" % (ocpcaprivate.token_description, token)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ("FAILED TO DELETE TOKEN DESCRIPTION")
      raise
    self.conn.commit()


  def deleteOCPCADatabase ( self, project ):
    #Used for the project management interface
#PYTODO - Check about function
    # Check if there are any tokens for this database
    sql = "SELECT count(*) FROM %s WHERE project=\'%s\'" % ( ocpcaprivate.projects,project )
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      logging.error ("Failed to query projects for database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to query projects for database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
    self.conn.commit()
    row = cursor.fetchone()
    if (row == None):
      # delete the database
      sql = "DROP DATABASE " + proj.getDBName()
      
      try:
        cursor = self.conn.cursor()
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      self.conn.commit()
    else:
      raise OCPCAError ("Tokens still exists. Failed to drop project database")

  def deleteDataset ( self, dataset ):
    #Used for the project management interface
#PYTODO - Check about function
    # Check if there are any tokens for this dataset    
    sql = "SELECT * FROM %s WHERE dataset=\'%s\'" % ( ocpcaprivate.projects, dataset )
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      logging.error ("Failed to query projects for dataset %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to query projects for dataset %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
    self.conn.commit()
    row = cursor.fetchone()
    if (row == None):
      sql = "DELETE FROM {0} WHERE dataset=\'{1}\'".format (ocpcaprivate.datasets,dataset)
      try:
        cursor = self.conn.cursor()
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to delete dataset %d : %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to delete dataset %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      self.conn.commit()
    else:
      raise OCPCAError ("Tokens still exists. Failed to drop project database")

  #
  #  getPublicTokens
  #
  def getPublic ( self ):
    """return a list of public tokens"""

    # RBTODO our notion of a public project is not good so far 
    sql = "select token from {} where public=1".format(ocpcaprivate.projects)
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      conn.rollback()
      logging.error ("Failed to query projects for public tokens %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to query projects for public tokens %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    return [item[0] for item in cursor.fetchall()]

