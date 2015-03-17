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
from contextlib import closing

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'

from ocpuser.models import Project
from ocpuser.models import Dataset
from ocpuser.models import Token
from ocpuser.models import Channel

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
# RB changes to VERSION from VERSION_NUMBER  -- it's not a number.  We'll want A.B.C.D type releases
OCP_VERSION = '0.6'
SCHEMA_VERSION = '0.6'

OCP_channeltypes = {0:'image',1:'annotation',2:'channel',3:'probmap',4:'timeseries'}

# channeltype groups
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

"""While this is not a true inheritance hierarchy from OCPCADataset->OPCPCAProject->OCPCAChannel
    modeling it as such makes it easier to call things on the channel.  It has dataset properties, etc."""

class OCPCADataset:
  """Configuration for a dataset"""

  def __init__ ( self, dataset ):
    """Construct a db configuration from the dataset parameters""" 
 
    self.ds = Dataset.objects.get(dataset_name=dataset)

    # nearisotropic service for Stephan
    self.nearisoscaledown = {}

    self.resolutions = []
    self.cubedim = {}
    self.imagesz = {}
    self.offset = {}
    self.voxelres = {}
    self.scalingoption = self.ds.scalingoption
    self.scalinglevels = self.ds.scalinglevels
    self.timerange = (self.ds.starttime, self.ds.endtime)

    for i in range (self.ds.scalinglevels+1):
      """Populate the dictionaries"""

      # add this level to the resolutions
      self.resolutions.append( i )

      # set the image size
      #  the scaled down image rounded up to the nearest cube
      xpixels=((self.ds.ximagesize-1)/2**i)+1
      ypixels=((self.ds.yimagesize-1)/2**i)+1
      if self.ds.scalingoption == ZSLICES:
        zpixels=self.ds.zimagesize
      else:
        zpixels=((self.ds.zimagesz-1)/2**i)+1
      self.imagesz[i] = [ xpixels, ypixels, zpixels ]

      # set the offset
      if self.ds.xoffset==0:
        xoffseti = 0
      else:
         xoffseti = ((self.ds.xoffset)/2**i)
      if self.ds.yoffset==0:
        yoffseti = 0
      else:
         yoffseti = ((self.ds.yoffset)/2**i)
      if self.ds.zoffset==0:
        zoffseti = 0
      else:
        if self.ds.scalingoption == ZSLICES:
          zoffseti = self.ds.zoffset
        else:
         zoffseti = ((self.ds.zoffset)/2**i)

      self.offset[i] = [ xoffseti, yoffseti, zoffseti ]

      # set the voxelresolution
      xvoxelresi = self.ds.xvoxelres*float(2**i)
      yvoxelresi = self.ds.yvoxelres*float(2**i)
      if self.ds.scalingoption == ZSLICES:
        zvoxelresi = self.ds.zvoxelres
      else:
        zvoxelresi = self.ds.zvoxelres*float(2**i)

      self.voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi ]

      # choose the cubedim as a function of the zscale
      #  this may need to be changed.  
      if self.ds.scalingoption == ZSLICES:
        if float(self.ds.zvoxelres/self.ds.xvoxelres)/(2**i) >  0.5:
          self.cubedim[i] = [128, 128, 16]
        else: 
          self.cubedim[i] = [64, 64, 64]

        # Make an exception for bock11 data -- just an inconsistency in original ingest
        if self.ds.ximagesize == 135424 and i == 5:
          self.cubedim[i] = [128, 128, 16]

      else:
        # RB what should we use as a cubedim?
        self.cubedim[i] = [128, 128, 16]
#        self.cubedim[i] = [64, 64, 64]


  def getDatasetDescription ( self ):
    return self.ds.dataset_description

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


class OCPCAProject:

  def __init__(self,token):
    self.tk = Token.objects.get(token_name=token)
    self.pr = Project.objects.get(project_name=self.tk.project_id)
    self.datasetcfg = OCPCADataset(self.pr.dataset_id)

  # Accessors
  def getToken ( self ):
    return self.tk.token_name
  def getDBHost ( self ):
      return self.pr.dbhost
  def getKVEngine ( self ):
    return self.pr.kvengine
  def getKVServer ( self ):
    return self.pr.kvserver
  def getDBName ( self ):
    return self.pr.project_name
  def getProjectName ( self ):
    return self.pr.project_name
  def getProjectDescription ( self ):
    return self.pr.project_description
  def getOCPVersion ( self ):
    return self.pr.ocp_version
  def getSchemaVersion ( self ):
    return self.pr.schema_version

  def projectChannels ( self ):
    """Return a generator of Channel Objects""" 
    chs = Channel.objects.filter(project_id=self.pr)
    for ch in chs:
      yield OCPCAChannel(self.tk.token_name, ch.channel_name)

  # Setters

  # accessors for RB to fix
  def getDBUser( self ):
    return ocpcaprivate.dbuser
  def getDBPasswd( self ):
    return ocpcaprivate.dbpasswd


class OCPCAChannel (OCPCAProject):

  def __init__(self, token, channel):
    """Constructor for a channel. It is a project and then some."""
    OCPCAProject.__init__(self,token)
    self.ch = Channel.objects.get(channel_name=channel, project=self.pr)

  def getDataType ( self ):
    return self.ch.channel_datatype
  def getChannelName ( self ):
    return self.ch.channel_name
  def getChannelType ( self ):
    return self.ch.channel_type
  def getChannelDescription ( self ):
    return self.ch.channel_description
  def getExceptions ( self ):
    return self.ch.exceptions
  def getReadOnly ( self ):
    return self.ch.readonly
  def getResolution ( self ):
    return self.ch.resolution
  def getWindowRange ( self ):
    return (self.ch.startwindow,self.ch.endwindow)
  def getPropagate ( self ):
    return self.ch.propagate

  def getIDsTbl ( self ):
    if self.pr.getOCPVersion() == '0.0':
      return "ids"
    else:
      return "{}_ids".format(self.ch.channel_name)


  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getOCPVersion() == '0.0':
      return "res{}".format(resolution)
    else:
      return "{}_res{}".format(self.ch.channel_name,resolution)

  def getNearIsoTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getOCPVersion() == '0.0':
      return "res{}neariso".format(resolution)
    else:
      return "{}_res{}neariso".format(self.ch.channel_name,resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    if self.pr.getOCPVersion() == '0.0':
      return "idx{}".format(resolution)
    else:
      return "{}_idx{}".format(self.ch.channel_name,resolution)

  def setPropagate ( self, value ):
    # 0 - Propagated
    # 1 - Under Propagation
    # 2 - UnPropagated
    if not self.getChannelType() == 'annotation':
      logger.error ( "Cannot set Propagate Value {} for a non-Annotation Project {}".format( value, self._token ) )
      raise OCPCAError ( "Cannot set Propagate Value {} for a non-Annotation Project {}".format( value, self._token ) )
    elif value in [NOT_PROPAGATED]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_FALSE )
    elif value in [UNDER_PROPAGATION,PROPAGATED]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_TRUE )
    else:
      logger.error ( "Wrong Propagate Value {} for Channel {}".format( value, self.ch.channel_name ) )
      raise OCPCAError ( "Wrong Propagate Value {} for Project {}".format( value, self.ch.channel_name ) )
  
  def setReadOnly ( self, value ):
    # 0 - Readonly
    # 1 - Not Readonly
    if value in [READONLY_TRUE,READONLY_FALSE]:
      self.ch.readonly = value
    else:
      logger.error ( "Wrong Readonly Value {} for Project {}".format( value, self._token ) )
      raise OCPCAError ( "Wrong Readonly Value {} for Project {}".format( value, self._token ) )

  def isPropagated ( self ):
    if self.ch.propagate in [PROPAGATED]:
      return True
    else:
      return False

class OCPCAProjectsDB:
  """Database for the annotation and cutout projects"""

  def __init__(self):
    """ Create the database connection """

    self.conn = MySQLdb.connect (host = ocpcaprivate.dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = ocpcaprivate.db ) 

  # for context lib closing
  def close (self):
    pass

  def newOCPCAProject ( self, project_name ):
    """Make the database for a project."""

    with closing(self.conn.cursor()) as cursor:

      try:
        # Make the database 
        sql = "CREATE DATABASE {}".format( project_name )
     
        cursor.execute ( sql )
        self.conn.commit()
      except MySQLdb.Error, e:
        logger.error ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise OCPCAError ("Failed to create database for new project %d: %s. sql=%s" % (e.args[0], e.args[1], sql))


  def newOCPCAChannel ( self, project_name, channel_name ):
    """Make the tables for a channel."""

    pr = Project.objects.get(project_name=project_name)
    ch = Channel.objects.get(channel_name=channel_name, project_id=project_name)
    ds = Dataset.objects.get(dataset_name=pr.dataset_id)

    # Connect to the database
    with closing (MySQLdb.connect (host = pr.host, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db = pr.project_name )) as conn:
      with closing(conn.cursor()) as cursor:

        try:

          if pr.kvengine == 'MySQL':

            if ch.channel_type not in ['timeseries']:

              for i in range(ds.scalinglevels+1): 
                cursor.execute ( "CREATE TABLE {}_res{} ( chanstr VARCHAR(255), zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.channel_name,i) )
              conn.commit()

            elif ch.channel_type == 'timeseries':

              for i in range(ds.scalinglevels+1): 
                cursor.execute ( "CREATE TABLE {}_res{} ( chanstr VARCHAR(255), zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(ch.channel_name,i) )
              conn.commit()

            else:
              assert(0) #RBTODO throw a big error

          elif pr.kvengine == 'Riak':

            #RBTODO figure out new schema for Riak
            rcli = riak.RiakClient(host=proj.getKVServer(), pb_port=8087, protocol='pbc')
            bucket = rcli.bucket_type("ocp{}".format(proj.getProjectType())).bucket(proj.getDBName())
            bucket.set_property('allow_mult',False)

          elif pr.kvengine == 'Cassandra':

            #RBTODO figure out new schema for Cassandra
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
          if ch.channel_type == 'annotation': 

            cursor.execute("CREATE TABLE {}_ids ( id BIGINT PRIMARY KEY)".format(ch.channel_name))

            # And the RAMON objects
            cursor.execute ( "CREATE TABLE {}_annotations (annoid BIGINT PRIMARY KEY, type INT, confidence FLOAT, status INT)".format(ch.channel_name))
            cursor.execute ( "CREATE TABLE {}_seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT)".format(ch.channel_name))
            cursor.execute ( "CREATE TABLE {}_synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT)".format(ch.channel_name))
            cursor.execute ( "CREATE TABLE {}_segments (annoid BIGINT PRIMARY KEY, segmentclass INT, parentseed INT, neuron INT)".format(ch.channel_name))
            cursor.execute ( "CREATE TABLE {}_organelles (annoid BIGINT PRIMARY KEY, organelleclass INT, parentseed INT, centroidx INT, centroidy INT, centroidz INT)".format(ch.channel_name))
            cursor.execute ( "CREATE TABLE {}_kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ))".format(ch.channel_name))

            conn.commit()

            if pr.kvengine == 'MySQL':
              for i in range(ds.scalinglevels+1):
                if ch.exceptions:
                  cursor.execute ( "CREATE TABLE {}_exc{} ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id))".format(ch.channel_name,i))
                cursor.execute ( "CREATE TABLE {}_idx{} ( annid BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.channel_name,i))

              conn.commit()

            elif pr.kvengine == 'Riak':
              pass

            elif pr.kvengine == 'Cassandra':

              cluster = Cluster( [pr.kvserver] )
              try:
                session = cluster.connect()
                session.execute ( "USE {}".format(pr.project_name))
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


  def deleteOCPCADB ( self, proj_name ):

    pr = Project.objects.get(project_name=proj_name)

    # delete the database
    sql = "DROP DATABASE " + pr.project_name

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

    if pr.kvengine == 'Cassandra':

      cluster = Cluster( [pr.kvserver] )
      try:
        session = cluster.connect()
        session.execute ( "DROP KEYSPACE {}".format(pr.project_name), timeout=30 )
      finally:
        cluster.shutdown()

    elif pr.kvengine == 'Riak':

      # connect to Riak
      rcli = riak.RiakClient(host=proj.kvserver, pb_port=8087, protocol='pbc')
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
    return OCPCADataset (dataset)

  def loadToken ( self, token ):
    """Query django configuration for a token to bind to a project"""
    return OCPCAProject (token)
   
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

