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
import os
import sys

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'

from ocpuser.models import Project
from ocpuser.models import Dataset
from ocpuser.models import Token

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

# OCP Version
OCP_VERSION_NUMBER = 0.6
SCHEMA_VERSION_NUMBER = 0.6

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

# Public Values
PUBLIC_TRUE = 1
PUBLIC_FALSE = 0

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
    pass

  #
  # Load the ocpca databse information based on the token
  #
  def loadToken ( self, token_to_load ):
    """ Load the annotation database information based on the token """

    try:

      token = Token.objects.get( token_name = token_to_load )
      project = Project.objects.get ( project_name = token.project_id )

      proj = OCPCAProject ( token.token_name, project.project_name.strip(), project.host, project.project_description, project.projecttype, project.datatype, project.dataset_id, project.overlayproject, project.overlayserver, token.readonly, project.exceptions, project.resolution, project.kvengine, project.kvserver, project.propagate ) 

      proj.datasetcfg = self.loadDatasetConfig ( project.dataset )

      return proj

    except MySQLdb.Error, e:
      logger.error ("Failed to load token %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise OCPCAError ("Failed to load token %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


  #
  # Load the ocpca databse information based on the project
  #
  def loadProject ( self, project_arg ):
    """ Load the annotation database information based on the project """

    proj = Project.objects.get ( project_name = project_arg )

    # Create a project object
    ocpproj = OCPCAProject ( "", proj.project_name.strip(), proj.host, proj.project_description, proj.projecttype, proj.datatype, proj.dataset, proj.overlayproject, proj.overlayserver, 0, proj.exceptions, proj.resolution, proj.kvengine, proj.kvserver, proj.propagate ) 

    ocpproj.datasetcfg = self.loadDatasetConfig ( ocpproj.getDataset() )

    return ocpproj

    

  def newOCPCADB ( self, project_name ):

    proj = self.loadProject ( project_name )
    datasetcfg = self.loadDatasetConfig ( proj.getDataset() )

    with closing(self.conn.cursor()) as cursor:
      try:
        # Make the database and associated ocpca tables
        sql = "CREATE DATABASE {}".format( project_name )
     
        cursor.execute ( sql )
        self.conn.commit()
      except MySQLdb.Error, e:
        logger.error ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Connect to the new database

    newconn = MySQLdb.connect (host = proj.getDBHost(), user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = project_name )
    newcursor = newconn.cursor()

    try:

      if proj.getKVEngine() == 'MySQL':

        # tables for annotations and images
        if proj.getProjectType() not in ['channel','timeseries']:

          for i in datasetcfg.resolutions: 
            newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
            #newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
          newconn.commit()

        elif proj.getProjectType() == 'timeseries':

          for i in datasetcfg.resolutions: 
            newcursor.execute ( "CREATE TABLE res{} ( zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(i) )
            #newcursor.execute ( "CREATE TABLE raw{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(i) )
            #newcursor.execute ( "CREATE TABLE timeseries%s ( z INT, y INT, x INT, t INT,  series LONGBLOB, PRIMARY KEY (z,y,x,t))"%i) 
          newconn.commit()

        # tables for channel dbs
        elif proj.getProjectType() == 'channel':

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
      if proj.getProjectType() == 'annotation': 

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
            if proj.getExceptions():
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


  def deleteOCPCADB ( self, proj_name ):

    proj = self.loadProject(proj_name) 

    # delete the database
    sql = "DROP DATABASE " + proj.getDBName()

    with closing(self.conn.cursor()) as cursor:
      try:
        cursor.execute ( sql )
        self.conn.commit()
      except MySQLdb.Error, e:
        self.conn.rollback()
        logger.error ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to drop project database %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


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

    dataset = Dataset.objects.get ( dataset_name = dataset )

    return OCPCADataset ((dataset.ximagesize, dataset.yimagesize, dataset.zimagesize), (dataset.xoffset, dataset.yoffset, dataset.zoffset), (dataset.xvoxelres, dataset.yvoxelres, dataset.zvoxelres), dataset.scalinglevels, dataset.scalingoption, dataset.startwindow, dataset.endwindow, dataset.starttime, dataset.endtime ) 

   
  #
  # Update the propagate  and readonly values for a project
  #
  def updatePropagate ( self, proj):
    """ """
    pr = Project.objects.get ( project_name=proj.getDBName() )
    tk = Token.objects.get ( token_name=proj.getToken() )
    tk.readonly = proj.getReadOnly()
    pr.propagate = proj.getPropagate()
    tk.save()
    pr.save()

  #
  #  getPublicTokens
  #
  def getPublic ( self ):
    """ Return a list of public tokens """

    # get public tokens
    tkns = Token.objects.filter(public=1)

    return [t.token_name for t in tkns]

