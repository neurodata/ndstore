# Licensed under the Apache License, Version 2.0 (the "License")
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

import MySQLdb
import h5py
import numpy as np
import math
from contextlib import closing

# need imports to be conditional
try:
  from cassandra.cluster import Cluster
except:
   pass
try:
  import riak
except:
   pass

import ocpcaprivate
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

OCP_databasetypes = {0:'image',1:'annotation',2:'channel',3:'probmap',4:'timeseries'}

# projecttype groups
IMAGE_PROJECTS = [ 'image', 'probmap' ]
CHANNEL_PROJECTS = [ 'channel' ]
TIMESERIES_PROJECTS = [ 'timeseries' ]
ANNOTATION_PROJECTS = [ 'annotation' ]
COMPOSITE_PROJECTS = CHANNEL_PROJECTS + TIMESERIES_PROJECTS

# datatype groups
DTYPE_uint8 = [ 'uint8' ]
DTYPE_uint16 = [ 'uint16' ]
DTYPE_uint32 = [ 'rgb32','uint32' ]
DTYPE_uint64 = [ 'rgb64' ]
DTYPE_float32 = [ 'probability' ]
OCP_dtypetonp = {'uint8':np.uint8,'uint16':np.uint16,'uint32':np.uint32,'rgb32':np.uint32,'rgb64':np.uint64,'probability':np.float32}

# Propagated Values
PROPAGATED = 2
UNDER_PROPAGATION = 1
NOT_PROPAGATED = 0

# ReadOnly Values
READONLY_TRUE = 1
READONLY_FALSE = 0

# SCALING OPTIONS
ZSLICES = 0
ISOTROPIC = 1

# Exception Values
EXCEPTION_TRUE = 1
EXCEPTION_FALSE = 0

class OCPCAProject:
  """ Project specific for cutout and annotation data """

  # Constructor 
  def __init__(self, token, dbname, dbhost, dbdescription, projecttype, datatype, dataset, overlayproject, overlayserver, readonly, exceptions, resolution, kvengine, kvserver, propagate ):
    """ Initialize the OCPCA Project """
    
    self._token = token
    self._dbname = dbname
    self._dbdescription = dbdescription
    self._dbhost = dbhost
    self._projecttype = projecttype
    self._dtype = datatype
    self._dataset = dataset
    self._projecttype = projecttype
    self._overlayproject = overlayproject
    self._overlayserver = overlayserver
    self._resolution = resolution
    self._readonly = readonly
    self._exceptions = exceptions    
    self._kvserver = kvserver
    self._kvengine = kvengine
    self._propagate = propagate

    # Could add these to configuration.  Probably remove res as tablebase instead
    self._ids_tbl = "ids"

  # Accessors
  def getToken ( self ):
    return self._token
  def getDBHost ( self ):
      return self._dbhost
  def getDataType ( self ):
    return self._dtype
  def getProjectType ( self ):
    return self._projecttype
  def getDBName ( self ):
    return self._dbname
  def getDataset ( self ):
    return self._dataset
  def getIDsTbl ( self ):
    return self._ids_tbl
  def getExceptions ( self ):
    return self._exceptions
  def getOverlayServer ( self ):
    return self._overlayserver
  def getOverlayProject ( self ):
    return self._overlayproject
  def getDBType ( self ):
    return self._projecttype
  def getReadOnly ( self ):
    return self._readonly
  def getResolution ( self ):
    return self._resolution
  def getKVEngine ( self ):
    return self._kvengine
  def getKVServer ( self ):
    return self._kvserver
  def getPropagate ( self ):
    return self._propagate

  # Setters
  def setPropagate ( self, value ):
    # 0 - Propagated
    # 1 - Under Propagation
    # 2 - UnPropagated
    if not self.getProjectType() == 'annotation':
      logger.error ( "Cannot set Propagate Value {} for a non-Annotation Project {}".format( value, self._token ) )
      raise OCPCAError ( "Cannot set Propagate Value {} for a non-Annotation Project {}".format( value, self._token ) )
    elif value in [NOT_PROPAGATED]:
      self._propagate = value
      self.setReadOnly ( READONLY_FALSE )
    elif value in [UNDER_PROPAGATION,PROPAGATED]:
      self._propagate = value
      self.setReadOnly ( READONLY_TRUE )
    else:
      logger.error ( "Wrong Propagate Value {} for Project {}".format( value, self._token ) )
      raise OCPCAError ( "Wrong Propagate Value {} for Project {}".format( value, self._token ) )
    
  
  def setReadOnly ( self, value ):
    # 0 - Readonly
    # 1 - Not Readonly
    if value in [READONLY_TRUE,READONLY_FALSE]:
      self._readonly = value
    else:
      logger.error ( "Wrong Readonly Value {} for Project {}".format( value, self._token ) )
      raise OCPCAError ( "Wrong Readonly Value {} for Project {}".format( value, self._token ) )


  def isPropagated ( self ):
    if self._propagate in [PROPAGATED]:
      return True
    else:
      return False

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

  def __init__ ( self, (ximagesz, yimagesz, zimagesz), (xoffset, yoffset, zoffset), (xvoxelres, yvoxelres, zvoxelres), scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime ):
    """Construct a db configuration from the dataset parameters""" 

    self.windowrange = [ startwindow, endwindow ]
    self.timerange = [ starttime, endtime ]

    # nearisotropic service for Stephan
    self.nearisoscaledown = {}

    self.resolutions = []
    self.cubedim = {}
    self.imagesz = {}
    self.offset = {}
    self.voxelres = {}
    self.scalingoption = scalingoption
    self.zoomlevels = scalinglevels

    for i in range (scalinglevels+1):
      """Populate the dictionaries"""

      # add this level to the resolutions
      self.resolutions.append( i )

      # set the image size
      #  the scaled down image rounded up to the nearest cube
      xpixels=((ximagesz-1)/2**i)+1
      ypixels=((yimagesz-1)/2**i)+1
      if scalingoption == ZSLICES:
        zpixels=zimagesz
      else:
        zpixels=((zimagesz-1)/2**i)+1
      self.imagesz[i] = [ xpixels, ypixels, zpixels ]

      # set the offset
      if xoffset==0:
        xoffseti = 0
      else:
         xoffseti = ((xoffset)/2**i)
      if yoffset==0:
        yoffseti = 0
      else:
         yoffseti = ((yoffset)/2**i)
      if zoffset==0:
        zoffseti = 0
      else:
        if scalingoption == ZSLICES:
          zoffseti = zoffset
        else:
         zoffseti = ((zoffset)/2**i)

      self.offset[i] = [ xoffseti, yoffseti, zoffseti ]

      # set the voxelresolution
      xvoxelresi = xvoxelres*float(2**i)
      yvoxelresi = yvoxelres*float(2**i)
      if scalingoption == ZSLICES:
        zvoxelresi = zvoxelres
      else:
        zvoxelresi = zvoxelres*float(2**i)

      self.voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi ]

      # choose the cubedim as a function of the zscale
      #  this may need to be changed.  
      if scalingoption == ZSLICES:
        if float(zvoxelres/xvoxelres)/(2**i) >  0.5:
          self.cubedim[i] = [128, 128, 16]
        else: 
          self.cubedim[i] = [64, 64, 64]

        # Make an exception for bock11 data -- just an inconsistency in original ingest
        if ximagesz == 135424 and i == 5:
          self.cubedim[i] = [128, 128, 16]

      else:
        # RB what should we use as a cubedim?
        self.cubedim[i] = [128, 128, 16]
#        self.cubedim[i] = [64, 64, 64]



      #RB need to reconsider nearisotropic for Stefan.....
#      # set the isotropic image size when well defined
#      if self.zscale[i] < 1.0:
#        self.isoslicerange[i] = [ startslice, startslice + int(math.floor((endslice-startslice+1)*self.zscale[i])) ]
#
#        # find the neareat to isotropic value
#        scalepixels = 1/self.zscale[i]
#        if ((math.ceil(scalepixels)-scalepixels)/scalepixels) <= ((scalepixels-math.floor(scalepixels))/scalepixels):
#          self.nearisoscaledown[i] = int(math.ceil(scalepixels))
#        else:
#          self.nearisoscaledown[i] = int(math.floor(scalepixels))
#
#      else:
#        self.isoslicerange[i] = self.slicerange
#        self.nearisoscaledown[i] = int(1)

  #
  #  Check that the specified arguments are legal
  #
  def checkCube ( self, resolution, corner, dim, tstart=0, tend=0 ):
    """Return true if the specified range of values is inside the cube"""

    [xstart, ystart, zstart ] = corner
    xend = xstart + dim[0]
    yend = ystart + dim[1]
    zend = zstart + dim[2]


    #KLTODO check the timeseries code here.
    if ( ( xstart >= 0 ) and ( xstart < xend) and ( xend <= self.imagesz[resolution][0]) and\
        ( ystart >= 0 ) and ( ystart < yend) and ( yend <= self.imagesz[resolution][1]) and\
        ( zstart >= 0 ) and ( zstart < zend) and ( zend <= self.imagesz[resolution][2]) and\
        ( tstart >= self.timerange[0]) and ((tstart < tend) or tstart==0 and tend==0) and (tend <= (self.timerange[1]+1))):
      return True
    else:
      return False

  
  #
  #  Check that the specified arguments are legal
  #
  def checkTimeSeriesCube ( self, tstart, tend, resolution, xstart, xend, ystart, yend, zstart, zend ):
    """Return true if the specified range of values is inside the timeseries cube"""

    [xstart, ystart, zstart ] = corner
    xend = xstart + dim[0]
    yend = ystart + dim[1]
    zend = zstart + dim[2]

    if ( ( xstart >= 0 ) and ( xstart < xend) and ( xend <= self.imagesz[resolution][0] ) and\
        ( ystart >= 0 ) and ( ystart < yend) and ( yend <= self.imagesz[resolution][1] ) and\
        ( zstart >= 0 ) and ( zstart < zend) and ( zend <= self.imagesz[resolution][2]) and\
        ( tstart >= self.timerange[0] ) and ( tstart < tend ) and ( tend <= (self.timerange[1]+1) ) )  :
      return True
    else:
      return False
  
  
  #
  #  Return the image size
  #
  def imageSize ( self, resolution ):
    return  [ self.imagesz [resolution], self.timerange ]


class OCPCAProjectsDB:
  """Database for the annotation and cutout projects"""

  def __init__(self):
    """ Create the database connection """

    self.conn = MySQLdb.connect (host = ocpcaprivate.dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = ocpcaprivate.db ) 


  # for context lib closing
  def close (self):
    self.conn.close()

  #
  # Load the ocpca databse information based on the token
  #
  def loadProject ( self, token ):
    """ Load the annotation database information based on the token """

#RBTODO what's up here???
    # Lookup the information for the database project based on the token
#    sql = "SELECT token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions, resolution , kvserver, kvengine, propagate from {} where token = \'{}\'".format(ocpcaprivate.projects, token)
    sql = "SELECT token_name, token_description, project_id, readonly, public from {} where token_name = \'{}\'".format(ocpcaprivate.tokens, token)
#=======
#    sql = "SELECT token, openid, host, project, projecttype, datatype, dataset, dataurl, readonly, exceptions, resolution , kvserver, kvengine, propagate from {} where token = \'{}\'".format(ocpcaprivate.projects, token)
#
#>>>>>>> rb-iso
    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
        # get the project information 
        row= cursor.fetchone()
      except MySQLdb.Error, e:
        logger.error ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # if the project is not found.  error
    if ( row == None ):
      logger.warning ( "Project token {} not found.".format( token ))
      raise OCPCAError ( "Project token {} not found.".format( token ))

    [token, token_description, project, readonly, public ] = row

    sql = "SELECT project_name, project_description, dataset_id, projecttype, datatype, overlayproject, overlayserver, resolution ,exceptions, host, kvengine, kvserver, propagate from {} where project_name = \'{}\'".format(ocpcaprivate.projects, project) 

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
        # get the project information                                                                                                                                                 
        row= cursor.fetchone()
      except MySQLdb.Error, e:
        logger.error ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        
        # if the project is not found.  error                                                                                                                                             
    if ( row == None ):
      logger.warning ( "Project token {} not found.".format( token ))
      raise OCPCAError ( "Project token {} not found.".format( token ))

    [ project_name, project_description, dataset, projecttype, datatype, overlayproject, overlayserver, resolution ,exceptions, host, kvengine, kvserver, propagate ] = row 


    # Create a project object
    proj = OCPCAProject ( token, project_name.strip(), host, project_description, projecttype, datatype, dataset, overlayproject, overlayserver, readonly, exceptions, resolution, kvengine, kvserver, propagate ) 

    proj.datasetcfg = self.loadDatasetConfig ( dataset )

    return proj

  #                                                                                                                                          
  # Load the ocpca databse information based on the token                                                                                        
  #
  def loadProjectDB ( self, project ):
    """ Load the annotation database information based on the token """

    # Lookup the information for the database project based on the token                                                                          
    sql = "SELECT project_name, project_description, dataset_id, projecttype, datatype, overlayproject, overlayserver, resolution, exceptions, host, kvengine, kvserver, propagate from {} where project_name = \'{}\'".format(ocpcaprivate.projects, project)

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
        # get the project information                                                                                                             
        row= cursor.fetchone()
      except MySQLdb.Error, e:
        logger.error ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not query ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # if the project is not found.  error                                                                                                         
    if ( row == None ):
      logger.warning ( "Project {} not found.".format( project ))
      raise OCPCAError ( "Project {} not found.".format( project ))

    [project_name, project_description, dataset, projecttype, datatype, overlayproject, overlayserver, resolution, exceptions, host, kvengine, kvserver, propagate ] = row
    
    #todo--not used
    readonly = 0;
    # Create a project object                                                                                                                     
    proj = OCPCAProject ("", project_name, host, project_description, projecttype, datatype, dataset, overlayproject, overlayserver, readonly, exceptions, resolution, kvengine, kvserver, propagate )
     # Lookup the information for the database project based on the token                                                                                             
    proj.datasetcfg = self.loadDatasetConfig ( dataset )

    return proj
    
  #
  # Create a new dataset
  #
  def newDataset ( self, dsname, imagesz, offset, voxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime ):
    """ Create a new ocpca dataset """

    sql = "INSERT INTO {0} (dataset_name, ximagesize, yimagesize, xoffset, yoffset, zoffset, xrvoxelres, yvoxelres, zvoxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\',\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\',\'{11}\',\'{12}\',\'{13}\',\'{14}\',\'{15}\',\'{16}\')".format (\
       ocpcaprivate.datasets, dsname, ximagesz, yimagesz, zimagesz, xoffset, yoffset, zoffset, xvoxelres, yvoxelres, zvoxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime )

    (ximagesz, yimagesz, zimagesz) = imagesz
    (xoffset, yoffset, zoffset) = offset
    (xvoxelres, yvoxelres, zvoxelres) = voxelres

#    sql = "INSERT INTO {0} (dataset, ximagesize, yimagesize, zimagesize, xoffset, yoffset, zoffset, xvoxelres, yvoxelres, zvoxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\',\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\',\'{11}\',\'{12}\',\'{13}\',\'{14}\',\'{15}\',\'{16}\')".format (\
#>>>>>>> rb-iso

    logger.info ( "Creating new dataset. Name %s. SQL=%s" % ( dsname, sql ))

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.error ("Could not query ocpca datsets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not query ocpca datsets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      self.conn.commit()


      #
      # Create a new Token
      #                                                                                                                                                                                                  
  def newToken ( self, token_name, token_description, project, readonly, public ):
    """ Create a new ocpca Token """

    sql = "INSERT INTO {0} (token_name, token_description, project_id, readonly, public) VALUES (\'{1}\',\'{2}\',\'{3}\',{4},{5})".format (ocpcaprivate.tokens, token_name, token_description, project, readonly, public )

    logger.info ( "Creating new Token. Name %s. SQL=%s" % ( token_name, sql ))

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.error ("Could not create new token %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not create new token %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      self.conn.commit()

    #
    # Create a new Project
    #                                                                                                                                                                                             
  def newProject ( self, project_name, project_description, userid, dataset, projecttype, datatype, overlayproject, overlayserver, resolution, exceptions, host, kvengine, kvserver, propagate ):
    """ Create a new ocpca Token """

    sql = "INSERT INTO {0} ( project_name, project_description, user_id, dataset_id, projecttype, datatype, overlayproject, overlayserver, resolution, exceptions, host, kvengine, kvserver, propagate ) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',\'{5}\',\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\',\'{11}\',\'{12}\',\'{13}\',\'{14}\')".format( ocpcaprivate.projects, project_name, project_description, userid, dataset, projecttype, datatype, overlayproject, overlayserver, resolution, int(exceptions), host, kvengine, kvserver, propagate  )

    logger.info ( "Creating new Project. Name %s. SQL=%s" % ( project_name, sql ))

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.error ("Could not create new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not create new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      self.conn.commit()

  #
  # Create a new project (annotation or data)
  #
  def newOCPCAProj ( self, token, token_description, userid, dbhost, project, projectdescription, projecttype, datatype, dataset, overlayproject, overlayserver, readonly, exceptions, nocreate, resolution, public, kvserver, kvengine, propagate ):
    """ Create a new ocpca project """
    
    datasetcfg = self.loadDatasetConfig ( dataset )
    self.newProject(project, projectdescription, userid, dataset, projecttype, datatype, overlayproject, overlayserver, resolution, exceptions, dbhost, kvengine, kvserver, propagate)
    self.newToken(token, token_description, project, readonly, public)

    proj = self.loadProject ( token )

    # Exception block around database creation
    try:

      # Make the database unless specified
      if not nocreate: 

        with closing(self.conn.cursor()) as cursor:
          try:
            # Make the database and associated ocpca tables
            sql = "CREATE DATABASE {}".format( project )
         
            cursor.execute ( sql )
            self.conn.commit()
          except MySQLdb.Error, e:
            logger.error ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
            raise OCPCAError ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


        # Connect to the new database

        newconn = MySQLdb.connect (host = dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = project )
        newcursor = newconn.cursor()

        try:

          if proj.getKVEngine() == 'MySQL':

            # tables for annotations and images
            if projecttype not in ['channel','timeseries']:

              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
                #newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
              newconn.commit()

            elif projecttype == 'timeseries':

              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(i) )
                #newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
                #newcursor.execute ( "CREATE TABLE timeseries%s ( z INT, y INT, x INT, t INT,  series LONGBLOB, PRIMARY KEY (z,y,x,t))"%i) 
              newconn.commit()

            # tables for channel dbs
            elif projecttype == 'timeseries':
              newcursor.execute ( 'CREATE TABLE channels ( chanstr VARCHAR(255), chanid INT, PRIMARY KEY(chanstr))')
              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( channel INT, zindex BIGINT, cube LONGBLOB, PRIMARY KEY(channel,zindex) )".format(i) )
              newconn.commit()

          elif proj.getKVEngine() == 'Riak':

            rcli = riak.RiakClient(host=proj.getKVServer(), pb_port=8087, protocol='pbc')
            bucket = rcli.bucket_type("ocp{}".format(proj.getProjectType())).bucket(proj.getDBName())
            bucket.set_property('allow_mult',False)

          elif proj.getKVEngine() == 'Cassandra':

            cluster = Cluster( [proj.getKVServer()] )
            try:
              session = cluster.connect()

              session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}".format(proj.getDBName()), timeout=30)
              session.execute ( "USE {}".format(proj.getDBName()) )
              session.execute ( "CREATE table cuboids ( resolution int, zidx bigint, cuboid text, PRIMARY KEY ( resolution, zidx ) )", timeout=30)
            except Exception, e:
              raise
            finally:
              cluster.shutdown()
            
          else:
            logging.error ("Unknown KV Engine requested: %s" % "RBTODO get name")
            raise OCPCAError ("Unknown KV Engine requested: %s" % "RBTODO get name")


          # tables specific to annotation projects
          if projecttype == 'annotation': 

            newcursor.execute("CREATE TABLE ids ( id BIGINT PRIMARY KEY)")

            # And the RAMON objects
            newcursor.execute ( "CREATE TABLE annotations (annoid BIGINT PRIMARY KEY, type INT, confidence FLOAT, status INT)")
            newcursor.execute ( "CREATE TABLE seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT)")
            newcursor.execute ( "CREATE TABLE synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT)")
            newcursor.execute ( "CREATE TABLE segments (annoid BIGINT PRIMARY KEY, segmentclass INT, parentseed INT, neuron INT)")
            newcursor.execute ( "CREATE TABLE organelles (annoid BIGINT PRIMARY KEY, organelleclass INT, parentseed INT, centroidx INT, centroidy INT, centroidz INT)")
            newcursor.execute ( "CREATE TABLE kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ))")

            newconn.commit()

            if proj.getKVEngine() == 'MySQL':
              for i in datasetcfg.resolutions: 
                if exceptions:
                  newcursor.execute ( "CREATE TABLE exc%s ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id))" % i )
                newcursor.execute ( "CREATE TABLE idx%s ( annid BIGINT PRIMARY KEY, cube LONGBLOB )" % i )

              newconn.commit()

            elif proj.getKVEngine() == 'Riak':
              pass

            elif proj.getKVEngine() == 'Cassandra':

              cluster = Cluster( [proj.getKVServer()] )
              try:
                session = cluster.connect()
                session.execute ( "USE {}".format(proj.getDBName()) )
                session.execute( "CREATE table exceptions ( resolution int, zidx bigint, annoid bigint, exceptions text, PRIMARY KEY ( resolution, zidx, annoid ) )", timeout=30)
                session.execute("CREATE table indexes ( resolution int, annoid bigint, cuboids text, PRIMARY KEY ( resolution, annoid ) )", timeout=30)
              except Exception, e:
                raise
              finally:
                cluster.shutdown()

        except MySQLdb.Error, e:
          logging.error ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise OCPCAError ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        except Exception, e:
          raise 
        finally:
          newcursor.close()
          newconn.close()

    # Error, undo the projects table entry
    except:
      sql = "DELETE FROM {0} WHERE token=\'{1}\'".format (ocpcaprivate.projects, token)

      logger.info ( "Could not create project database.  Undoing projects insert. Project %s. SQL=%s" % ( project, sql ))

      with closing(self.conn.cursor()) as cursor:
        try:
          cursor.execute ( sql )
          self.conn.commit()
        except MySQLdb.Error, e:
          logger.error ("Could not undo insert into ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          logger.error ("Check project database for project not linked to database.")
          raise

        # RBTODO drop tables here?

  #
  # Create a new project database (annotation or data)
  #
  def newOCPCAProjectDB ( self, project, description, dataset, projecttype ,resolution, exceptions, dbhost, kvserver, kvengine, propagate, nocreate ):
    """ Create a new ocpca project """

    datasetcfg = self.loadDatasetConfig ( dataset.dataset_name )
    
    proj = self.loadProjectDB ( project )

    # Exception block around database creation
    try:

      # Make the database unless specified
      if not nocreate:
        #Set up a new connection because we may be creating a remote database
        newconn = MySQLdb.connect (host = dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd )

        with closing(newconn.cursor()) as cursor:
          try:
            # Make the database and associated ocpca tables
            sql = "CREATE DATABASE {}".format( project )
         
            cursor.execute ( sql )
            newconn.commit()
          except MySQLdb.Error, e:
            logger.error ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
            raise OCPCAError ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


        # Connect to the new database

        newconn = MySQLdb.connect (host = dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = project )
        newcursor = newconn.cursor()

        try:

          if proj.getKVEngine() == 'MySQL':

            # tables for annotations and images
            if projecttype not in CHANNEL_DATASETS + TIMESERIES_DATASETS :

              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
                newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
              newconn.commit()

            elif projecttype in TIMESERIES_DATASETS :

              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(i) )
                newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
                #newcursor.execute ( "CREATE TABLE timeseries%s ( z INT, y INT, x INT, t INT,  series LONGBLOB, PRIMARY KEY (z,y,x,t))"%i) 
              newconn.commit()

            # tables for channel dbs
            elif projecttype in CHANNEL_DATASETS :
              newcursor.execute ( 'CREATE TABLE channels ( chanstr VARCHAR(255), chanid INT, PRIMARY KEY(chanstr))')
              for i in datasetcfg.resolutions: 
                newcursor.execute ( "CREATE TABLE res{} ( channel INT, zindex BIGINT, cube LONGBLOB, PRIMARY KEY(channel,zindex) )".format(i) )
              newconn.commit()

          elif proj.getKVEngine() == 'Riak':

            rcli = riak.RiakClient(host=proj.getKVServer(), pb_port=8087, protocol='pbc')
            bucket = rcli.bucket_type("ocp{}".format(proj.getDBType())).bucket(proj.getDBName())
            bucket.set_property('allow_mult',False)

          elif proj.getKVEngine() == 'Cassandra':

            cluster = Cluster( [proj.getKVServer()] )
            try:
              session = cluster.connect()

              session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}".format(proj.getDBName()), timeout=30)
              session.execute ( "USE {}".format(proj.getDBName()) )
              session.execute ( "CREATE table cuboids ( resolution int, zidx bigint, cuboid text, PRIMARY KEY ( resolution, zidx ) )", timeout=30)
            except Exception, e:
              raise
            finally:
              cluster.shutdown()
            
          else:
            logging.error ("Unknown KV Engine requested: %s" % "RBTODO get name")
            raise OCPCAError ("Unknown KV Engine requested: %s" % "RBTODO get name")


          # tables specific to annotation projects
          if projecttype in ANNOTATION_DATASETS :

            newcursor.execute("CREATE TABLE ids ( id BIGINT PRIMARY KEY)")

            # And the RAMON objects
            newcursor.execute ( "CREATE TABLE annotations (annoid BIGINT PRIMARY KEY, type INT, confidence FLOAT, status INT)")
            newcursor.execute ( "CREATE TABLE seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT)")
            newcursor.execute ( "CREATE TABLE synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT)")
            newcursor.execute ( "CREATE TABLE segments (annoid BIGINT PRIMARY KEY, segmentclass INT, parentseed INT, neuron INT)")
            newcursor.execute ( "CREATE TABLE organelles (annoid BIGINT PRIMARY KEY, organelleclass INT, parentseed INT, centroidx INT, centroidy INT, centroidz INT)")
            newcursor.execute ( "CREATE TABLE kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ))")

            newconn.commit()

            if proj.getKVEngine() == 'MySQL':
              for i in datasetcfg.resolutions: 
                if exceptions:
                  newcursor.execute ( "CREATE TABLE exc%s ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id))" % i )
                newcursor.execute ( "CREATE TABLE idx%s ( annid BIGINT PRIMARY KEY, cube LONGBLOB )" % i )

              newconn.commit()

            elif proj.getKVEngine() == 'Riak':
              pass

            elif proj.getKVEngine() == 'Cassandra':

              cluster = Cluster( [proj.getKVServer()] )
              try:
                session = cluster.connect()
                session.execute ( "USE {}".format(proj.getDBName()) )
                session.execute( "CREATE table exceptions ( resolution int, zidx bigint, annoid bigint, exceptions text, PRIMARY KEY ( resolution, zidx, annoid ) )", timeout=30)
                session.execute("CREATE table indexes ( resolution int, annoid bigint, cuboids text, PRIMARY KEY ( resolution, annoid ) )", timeout=30)
              except Exception, e:
                raise
              finally:
                cluster.shutdown()

        except MySQLdb.Error, e:
          logging.error ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise OCPCAError ("Failed to create tables for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        except Exception, e:
          raise 
        finally:
          newcursor.close()
          newconn.close()

    # Error, undo the projects table entry
    except:
      sql = "DELETE FROM {0} WHERE project_name=\'{1}\'".format (ocpcaprivate.projects, project)

      logger.info ( "Could not create project database.  Undoing projects insert. Project %s. SQL=%s" % ( project, sql ))

      with closing(self.conn.cursor()) as cursor:
        try:
          cursor.execute ( sql )
          self.conn.commit()
        except MySQLdb.Error, e:
          logger.error ("Could not undo insert into ocpca projects database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          logger.error ("Check project database for project not linked to database.")
          raise

        # RBTODO drop tables here?


  def deleteOCPCAToken ( self, token ):
    """ Delete an existing ocpca project """

    sql = "DELETE FROM {} WHERE token_name=\'{}\'".format( ocpcaprivate.tokens, token ) 

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      self.conn.commit()


  def deleteOCPCAProj ( self, project ):
    """ Delete an existing ocpca project """

    sql = "DELETE FROM {} WHERE project_name=\'{}\'".format( ocpcaprivate.projects, project ) 

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to remove project from projects tables %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      self.conn.commit()


  def deleteOCPCADB ( self, token ):

    # load the project
    try:

      proj = self.loadProject ( token )
      # delete line from projects table and tokens table
      self.deleteOCPCAToken ( token )
      self.deleteOCPCAProj ( proj.getDBName() )

    except Exception, e:
      logger.warning ("Failed to delete project {}".format(e))
      raise
      

    #  try to delete the database anyway
    #  Sometimes weird crashes can get stuff out of sync

    # delete the database
    sql = "DROP DATABASE " + proj.getDBName()

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
        self.conn.commit()
      except MySQLdb.Error, e:
        conn.rollback()
        logger.error ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#        raise OCPCAError ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


    #  try to delete the database anyway
    #  Sometimes weird crashes can get stuff out of sync

    if proj.getKVEngine() == 'Cassandra':

      cluster = Cluster( [proj.getKVServer()] )
      try:
        session = cluster.connect()
        session.execute ( "DROP KEYSPACE {}".format(proj.getDBName()), timeout=30 )
      finally:
        cluster.shutdown()


    elif proj.getKVEngine() == 'Riak':

      # connect to Riak
      rcli = riak.RiakClient(host=proj.getKVServer(), pb_port=8087, protocol='pbc')
      bucket = rcli.bucket_type("ocp{}".format(proj.getProjectType())).bucket(proj.getDBName())

      key_list = rcli.get_keys(bucket)

      for k in key_list:
        bucket.delete(k)


  # accessors for RB to fix
  def getDBUser( self ):
    return ocpcaprivate.dbuser
  def getDBPasswd( self ):
    return ocpcaprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res{}".format(resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx{}".format(resolution)

  def loadDatasetConfig ( self, dataset ):
    """Query the database for the dataset information and build a db configuration"""
    sql = "SELECT dataset_name, ximagesize, yimagesize, zimagesize, xoffset, yoffset, zoffset, xvoxelres, yvoxelres, zvoxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime from {} where dataset_name = \'{}\'".format( ocpcaprivate.datasets, dataset )

    with closing(self.conn.cursor()) as cursor:
      try:
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

    [ dataset, ximagesz, yimagesz, zimagesz, xoffset, yoffset, zoffset, xvoxelres, yvoxelres, zvoxelres, scalinglevels, scalingoption, startwindow, endwindow, starttime, endtime ] = row

    return OCPCADataset ( (int(ximagesz),int(yimagesz),int(zimagesz)), (int(xoffset),int(yoffset),int(zoffset)), (int(xvoxelres),int(yvoxelres),int(zvoxelres)), int(scalinglevels), int(scalingoption), int(startwindow), int(endwindow), int(starttime), int(endtime) ) 

  #
  # Load the ocpca databse information based on openid
  #
  def getFilteredProjects ( self, openid, filterby, filtervalue ):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    #url = "SELECT * from %s where " + filterby
    #sql = "SELECT * from %s where %s = \'%s\'" % (ocpcaprivate.table, filterby, filtervalue)
    token_desc = ocpcaprivate.token_description
    proj_tbl = ocpcaprivate.projects
    if (filterby == ""):
      sql = "SELECT * from %s LEFT JOIN %s on %s.token = %s.token where %s.openid = \'%s\' ORDER BY project" % (ocpcaprivate.projects,token_desc,proj_tbl,token_desc,proj_tbl,openid)
    else:
      sql = "SELECT * from %s LEFT JOIN %s on %s.token = %s.token where %s.openid = \'%s\' and %s.%s = \'%s\' ORDER BY project" % (ocpcaprivate.projects,token_desc,proj_tbl,token_desc, proj_tbl,openid, proj_tbl,filterby, filtervalue.strip())

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:

        logger.error ("Could not query ocpca datasets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Could not query ocpca datasets database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      # get the project information                                                                                                                                                                  
      row = cursor.fetchone()

    # if the project is not found.  error                                                                                                                                                            
    if ( row == None ):
      logger.warning ( "Dataset id %s not found." % ( dataset ))
      raise OCPCAError ( "Dataset id  %s not found." % ( dataset ))

    [ dataset ] = row
    return dataset


  #
  # Load Projects created by user ( projadmin)
  #
  def getDatasets ( self):
    """Load the annotation database information based on the openid"""
    # Lookup the information for the database project based on the openid
    sql = "SELECT * from {}".format( ocpcaprivate.datasets )

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
         logger.error ("FAILED TO FILTER")
         raise
      # get the project information

      row = cursor.fetchall()
    return row

   

  #
  # Update the propagate  and readonly values for a project
  #
  def updatePropagate ( self, proj):
    """ """
    sql = "UPDATE {} SET propagate = \'{}\', readonly = \'{}\' where token = \'{}\'".format( ocpcaprivate.projects, proj.getPropagate(), proj.getReadOnly(), proj.getToken())

    
    with closing(self.conn.cursor()) as cursor:
      try:
        self.conn.cursor().execute( sql )
      except MySQLdb.Error, e:
        logger.error ("Failed To Update Value of Propagate")
        raise

      self.conn.commit()

 


  def deleteOCPCADatabase ( self, project ):
    #Used for the project management interface
    # Check if there are any tokens for this database
    sql = "SELECT * FROM {} where project_name = \'{}\'".format(ocpcaprivate.projects, project)

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to query projects for database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to query projects for database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      self.conn.commit()
      row = cursor.fetchone()
      
      if (row == None):
        # delete the database
        sql = "DROP DATABASE " + project
        
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          conn.rollback()
          logging.error ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise OCPCAError ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        self.conn.commit()
      else:
        raise OCPCAError (" Failed to drop project database")


  def deleteDataset ( self, dataset ):
    #Used for the project management interface
    #PYTODO - Check about function
    # Check if there are any tokens for this dataset    
    sql = "SELECT * FROM {} WHERE dataset_name=\'{}\'".format( ocpcaprivate.projects, dataset )

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to query projects for dataset %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to query projects for dataset %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      self.conn.commit()
      row = cursor.fetchone()
      if (row == None):
        sql = "DELETE FROM {0} WHERE dataset_name=\'{1}\'".format (ocpcaprivate.datasets,dataset)
        try:
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
    """ Return a list of public tokens """

    # RBTODO our notion of a public project is not good so far 
    sql = "select token_name from {} where public=1".format(ocpcaprivate.tokens)

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        conn.rollback()
        logging.error ("Failed to query projects for public tokens %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to query projects for public tokens %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      return [item[0] for item in cursor.fetchall()]

