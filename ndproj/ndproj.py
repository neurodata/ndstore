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

import math
import MySQLdb
import numpy as np
from contextlib import closing
from operator import add, mul

# need imports to be conditional
try:
  from cassandra.cluster import Cluster
except:
   pass
try:
  import riak
except:
   pass
try:
  import boto3
except:
  pass

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from nduser.models import Project
from nduser.models import Dataset
from nduser.models import Token
from nduser.models import Channel
import annotation
from ndtype import IMAGE_CHANNELS, ANNOTATION_CHANNELS, ZSLICES, ISOTROPIC, READONLY_TRUE, READONLY_FALSE, PUBLIC_TRUE, NOT_PROPAGATED, UNDER_PROPAGATION, PROPAGATED, IMAGE, ANNOTATION, TIMESERIES, MYSQL, CASSANDRA, RIAK, DYNAMODB, REDIS,  ND_servermap, SUPERCUBESIZE

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")


"""While this is not a true inheritance hierarchy from NDDataset->OPCPCAProject->NDChannel modeling it as such makes it easier to call things on the channel.  It has dataset properties, etc."""

class NDDataset:
  """Configuration for a dataset"""

  def __init__ ( self, dataset_name ):
    """Construct a db configuration from the dataset parameters""" 
    
    try:
      self.ds = Dataset.objects.get(dataset_name = dataset_name)
    except ObjectDoesNotExist, e:
      logger.warning ( "Dataset {} does not exist. {}".format(dataset_name, e) )
      raise NDWSError ( "Dataset {} does not exist".format(dataset_name) )

    self.resolutions = []
    self.cubedim = {}
    self.supercubedim = {}
    self.imagesz = {}
    self.offset = {}
    self.voxelres = {}
    self.scale = {}
    self.scalingoption = self.ds.scalingoption
    self.scalinglevels = self.ds.scalinglevels
    self.timerange = (self.ds.starttime, self.ds.endtime)
    # nearisotropic service for Stephan
    self.nearisoscaledown = {}
    self.neariso_voxelres = {}
    self.neariso_imagesz = {}
    self.neariso_offset = {}

    for i in range (self.ds.scalinglevels+1):
      """Populate the dictionaries"""

      # add this level to the resolutions
      self.resolutions.append( i )

      # set the image size
      #  the scaled down image rounded up to the nearest cube
      xpixels = ((self.ds.ximagesize-1)/2**i)+1
      ypixels = ((self.ds.yimagesize-1)/2**i)+1
      if self.ds.scalingoption == ZSLICES:
        zpixels = self.ds.zimagesize
      else:
        zpixels = ((self.ds.zimagesize-1)/2**i)+1
      self.imagesz[i] = [ xpixels, ypixels, zpixels ]

      # set the offset
      xoffseti = 0 if self.ds.xoffset==0 else ((self.ds.xoffset)/2**i)
      yoffseti = 0 if self.ds.yoffset==0 else ((self.ds.yoffset)/2**i)
      if self.ds.zoffset == 0:
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
      zvoxelresi = self.ds.zvoxelres if self.ds.scalingoption == ZSLICES else self.ds.zvoxelres*float(2**i)

      self.voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi ]
      self.scale[i] = { 'xy':xvoxelresi/yvoxelresi , 'yz':zvoxelresi/xvoxelresi, 'xz':zvoxelresi/yvoxelresi }
      
      # choose the cubedim as a function of the zscale
      #self.cubedim[i] = [128, 128, 16]
      # this may need to be changed.  
      if self.ds.scalingoption == ZSLICES:
        #self.cubedim[i] = [512, 512, 16]
        self.cubedim[i] = [128, 128, 16]
        if float(self.ds.zvoxelres/self.ds.xvoxelres)/(2**i) >  0.5:
          self.cubedim[i] = [128, 128, 16]
        else: 
          self.cubedim[i] = [64, 64, 64]

        # Make an exception for bock11 data -- just an inconsistency in original ingest
        if self.ds.ximagesize == 135424 and i == 5:
          self.cubedim[i] = [128, 128, 16]
      else:
        # RB what should we use as a cubedim?
        self.cubedim[i] = [512, 512, 16]
      
      self.supercubedim[i] = map(mul, self.cubedim[i], SUPERCUBESIZE)

      if self.scale[i]['xz'] < 1.0:
        scalepixels = 1/self.scale[i]['xz']
        if ((math.ceil(scalepixels)-scalepixels)/scalepixels) <= ((scalepixels-math.floor(scalepixels))/scalepixels):
          self.nearisoscaledown[i] = int(math.ceil(scalepixels))
        else:
          self.nearisoscaledown[i] = int(math.floor(scalepixels))
      else:
        self.nearisoscaledown[i] = int(1)
      
      self.neariso_imagesz[i] = [ xpixels, ypixels, zpixels/self.nearisoscaledown[i] ]
      self.neariso_voxelres[i] = [ xvoxelresi, yvoxelresi, zvoxelresi*self.nearisoscaledown[i] ]
      self.neariso_offset[i] = [ float(xoffseti), float(yoffseti), float(zoffseti)/self.nearisoscaledown[i] ]


  # Accessors
  def getDatasetName(self):
    return self.ds.dataset_name
  def getResolutions(self):
    return self.resolutions
  def getPublic(self):
    return self.ds.public
  def getImageSize(self):
    return self.imagesz
  def getOffset(self):
    return self.offset
  def getScale(self):
    return self.scale
  def getVoxelRes(self):
    return self.voxelres
  def getCubeDims(self):
    return self.cubedim
  def getSuperCubeDims(self):
    return self.supercubedim
  def getSuperCubeSize(self):
    return SUPERCUBESIZE
  def getTimeRange(self):
    return self.timerange
  def getDatasetDescription ( self ):
    return self.ds.dataset_description

  def checkCube (self, resolution, corner, dim, timeargs=[0,0]):
    """Return true if the specified range of values is inside the cube"""

    [xstart, ystart, zstart ] = corner
    [tstart, tend] = timeargs

    [xend, yend, zend] = map(add, corner, dim) 

    if ( ( xstart >= 0 ) and ( xstart < xend) and ( xend <= self.imagesz[resolution][0]) and\
        ( ystart >= 0 ) and ( ystart < yend) and ( yend <= self.imagesz[resolution][1]) and\
        ( zstart >= 0 ) and ( zstart < zend) and ( zend <= self.imagesz[resolution][2]) and\
        ( tstart >= self.timerange[0]) and ((tstart < tend) or tstart==0 and tend==0) and (tend <= (self.timerange[1]+1))):
      return True
    else:
      return False

  def imageSize ( self, resolution ):
    """Return the image size"""
    return  [ self.imagesz [resolution], self.timerange ]


class NDProject:

  def __init__(self, token_name ) :

    if isinstance(token_name, str) or isinstance(token_name, unicode):
      try:
        self.tk = Token.objects.get(token_name = token_name)
        self.pr = Project.objects.get(project_name = self.tk.project_id)
        self.datasetcfg = NDDataset(self.pr.dataset_id)
      except ObjectDoesNotExist, e:
        logger.warning ( "Token {} does not exist. {}".format(token_name, e) )
        raise NDWSError ( "Token {} does not exist".format(token_name) )
    elif isinstance(token_name, Project):
      # Constructor for NDProject from Project Name
      try:
        self.tk = None
        self.pr = token_name
        self.datasetcfg = NDDataset(self.pr.dataset_id)
      except ObjectDoesNotExist, e:
        logger.warning ( "Token {} does not exist. {}".format(token_name, e) )
        raise NDWSError ( "Token {} does not exist".format(token_name) )

  # Accessors
  def getToken ( self ):
    return self.tk.token_name
  def getDBHost ( self ):
      return self.pr.host
  def getKVEngine ( self ):
    return self.pr.kvengine
  def getKVServer ( self ):
    return self.pr.kvserver
  def getMDEngine ( self ):
    return self.pr.mdengine
  def getDBName ( self ):
    return self.pr.project_name
  def getProjectName ( self ):
    return self.pr.project_name
  def getProjectDescription ( self ):
    return self.pr.project_description
  def getNDVersion ( self ):
    return self.pr.nd_version
  def getSchemaVersion ( self ):
    return self.pr.schema_version

  def projectChannels ( self, channel_list=None ):
    """Return a generator of Channel Objects"""
    if channel_list is None:
      chs = Channel.objects.filter(project_id=self.pr)
    else:
      chs = channel_list
    for ch in chs:
      yield NDChannel(self, ch.channel_name)

  def getChannelObj ( self, channel_name='default' ):
    """Returns a object for that channel"""
    if channel_name == 'default':
      channel_name = Channel.objects.get(project_id=self.pr, default=True)
    return NDChannel(self, channel_name)

  def getDBUser( self ):
    return settings.DATABASES['default']['USER']
  def getDBPasswd( self ):
    return settings.DATABASES['default']['PASSWORD']


class NDChannel:

  def __init__(self, proj, channel_name = None):
    """Constructor for a channel. It is a project and then some."""
    try:
      self.pr = proj
      self.ch = Channel.objects.get(channel_name = channel_name, project=self.pr.getProjectName())
    except ObjectDoesNotExist, e:
      logger.warning ( "Channel {} does not exist. {}".format(channel_name, e) )
      raise NDWSError ( "Channel {} does not exist".format(channel_name) )

  def getChannelModel ( self ):
    return Channel.objects.get(channel_name=self.ch.channel_name, project=self.pr.getProjectName())
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
  def getReadOnly (self):
    return self.ch.readonly
  def getResolution (self):
    return self.ch.resolution
  def getWindowRange (self):
    return [self.ch.startwindow,self.ch.endwindow]
  def getPropagate (self):
    return self.ch.propagate
  def isDefault (self):
    return self.ch.default 

  def getIdsTable (self):
    if self.pr.getNDVersion() == '0.0':
      return "ids"
    else:
      return "{}_ids".format(self.ch.channel_name)

  def getTable (self, resolution):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "res{}".format(resolution)
    else:
      if self.pr.getKVEngine() == MYSQL:
        return "{}_res{}".format(self.ch.channel_name, resolution)
      elif self.pr.getKVEngine() == CASSANDRA:
        return "{}_{}".format(self.ch.channel_name, 'cuboids')
      elif self.pr.getKVEngine() == DYNAMODB:
        return "{}_{}".format(self.ch.channel_name, 'cuboids')

  def getNearIsoTable (self, resolution):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "res{}neariso".format(resolution)
    else:
      return "{}_res{}neariso".format(self.ch.channel_name, resolution)

  def getKVTable (self, resolution):
    """Return the appropriate KvPairs for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "kvpairs{}".format(resolution)
    else:
      return "{}_kvpairs{}".format(self.ch.channel_name, resolution)
  
  def getIdxTable (self, resolution):
    """Return the appropriate Index table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "idx{}".format(resolution)
    else:
      if self.pr.getKVEngine() == MYSQL:
        return "{}_idx{}".format(self.ch.channel_name, resolution)
      elif self.pr.getKVEngine() == CASSANDRA:
        return "{}_{}".format(self.ch.channel_name, 'indexes')
      elif self.pr.getKVEngine() == DYNAMODB:
        return "{}_{}".format(self.ch.channel_name, 'indexes')

  def getAnnoTable (self, anno_type):
    """Return the appropriate table for the specified type"""
    if self.pr.getNDVersion() == '0.0':
      return "{}".format(annotation.anno_dbtables[anno_type])
    else:
      return "{}_{}".format(self.ch.channel_name, annotation.anno_dbtables[anno_type])

  def getExceptionsTable (self, resolution):
    """Return the appropiate exceptions table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "exc{}".format(resolution)
    else:
      return "{}_exc{}".format(self.ch.channel_name, resolution)

  def setPropagate (self, value):
    if value in [NOT_PROPAGATED, PROPAGATED]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_FALSE )
      self.ch.save()
    elif value in [UNDER_PROPAGATION]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_TRUE )
      self.ch.save()
    else:
      logger.error ( "Wrong Propagate Value {} for Channel {}".format( value, self.ch.channel_name ) )
      raise NDWSError ( "Wrong Propagate Value {} for Channel {}".format( value, self.ch.channel_name ) )
  
  def setReadOnly (self, value):
    if value in [READONLY_TRUE, READONLY_FALSE]:
      self.ch.readonly = value
      self.ch.save()
    else:
      logger.error ( "Wrong Readonly Value {} for Channel {}".format( value, self.channel_name ) )
      raise NDWSError ( "Wrong Readonly Value {} for Channel {}".format( value, self.ch.channel_name ) )

  def isPropagated (self):
    if self.ch.propagate in [PROPAGATED]:
      return True
    else:
      return False

class NDProjectsDB:
  """Database for the projects"""

  def __init__(self):
    """Create the database connection"""

    self.conn = MySQLdb.connect (host = settings.DATABASES['default']['HOST'], user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = settings.DATABASES['default']['NAME']) 

  # for context lib closing
  def close (self):
    pass

  def newNDProject ( self, project_name ):
    """Make the database for a project."""

    pr = Project.objects.get(project_name=project_name)

    if pr.kvengine == MYSQL:
      with closing(MySQLdb.connect (host = pr.host , user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'])) as conn:
        with closing(conn.cursor()) as cursor:

          try:
            # Make the database 
            sql = "CREATE DATABASE {}".format(pr.project_name)
         
            cursor.execute ( sql )
            conn.commit()
          except MySQLdb.Error, e:
            logger.error ("Failed to create database for new project {}: {}. sql={}".format(e.args[0], e.args[1], sql))
            raise NDWSError ("Failed to create database for new project {}: {}. sql={}".format(e.args[0], e.args[1], sql))
    
    elif pr.kvengine == CASSANDRA:
      
      try:
        server_address = ND_servermap[pr.kvserver]
        cluster = Cluster([server_address])
        session = cluster.connect()
        if server_address == 'localhost':  
          session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 0 }}".format(pr.project_name), timeout=30)
        else:
          session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}".format(pr.project_name), timeout=30)
      except Exception, e:
        pr.delete()
        logger.error("Failed to create namespace for new project {}".format(project_name))
        raise NDWSError("Failed to create namespace for new project {}".format(project_name))
      finally:
        session.shutdown()

    elif pr.kvengine in [DYNAMODB, REDIS]:
      # nothing to do, WOW!
      pass
    
    else:
      logging.error ("Unknown KV Engine requested: {}".format("RBTODO get name"))
      raise NDWSError ("Unknown KV Engine requested: {}".format("RBTODO get name"))


  def newNDChannel ( self, project_name, channel_name ):
    """Make the tables for a channel."""

    pr = Project.objects.get(project_name=project_name)
    ch = Channel.objects.get(channel_name=channel_name, project_id=project_name)
    ds = Dataset.objects.get(dataset_name=pr.dataset_id)

    # Connect to the database

    if pr.kvengine == MYSQL:
      with closing (MySQLdb.connect(host = pr.host, user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = pr.project_name)) as conn:
        with closing(conn.cursor()) as cursor:
          
          try:
            # tables specific to all other non time data
            if ch.channel_type not in [TIMESERIES]:
              for i in range(ds.scalinglevels+1): 
                cursor.execute ( "CREATE TABLE {}_res{} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.channel_name,i) )
            # tables specific to timeseries data
            elif ch.channel_type == TIMESERIES:
              for i in range(ds.scalinglevels+1): 
                cursor.execute ( "CREATE TABLE {}_res{} ( zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(ch.channel_name,i) )
            else:
              raise NDWSError("Channel type {} does not exist".format(ch.channel_type()))
            
            # tables specific to annotation projects
            if ch.channel_type == ANNOTATION: 
              cursor.execute("CREATE TABLE {}_ids ( id BIGINT PRIMARY KEY)".format(ch.channel_name))
              # And the RAMON objects
              cursor.execute ( "CREATE TABLE {}_ramon ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ))".format(ch.channel_name))
              for i in range(ds.scalinglevels+1):
                cursor.execute ( "CREATE TABLE {}_exc{} ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id))".format(ch.channel_name,i))
                cursor.execute ( "CREATE TABLE {}_idx{} ( annid BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.channel_name,i))
           
            # Commiting at the end
            conn.commit()
          except MySQLdb.Error, e:
            ch.delete()
            logging.error ("Failed to create tables for new project {}: {}.".format(e.args[0], e.args[1]))
            raise NDWSError ("Failed to create tables for new project {}: {}.".format(e.args[0], e.args[1]))

    elif pr.kvengine == RIAK:
      #RBTODO figure out new schema for Riak
      rcli = riak.RiakClient(host=pr.kvserver, pb_port=8087, protocol='pbc')
      bucket = rcli.bucket_type("nd{}".format(proj.getProjectType())).bucket(proj.getDBName())
      bucket.set_property('allow_mult',False)

    elif pr.kvengine == CASSANDRA:
      try:
        if ch.channel_type not in [TIMESERIES]:
          cluster = Cluster([pr.kvserver])
          session = cluster.connect(pr.project_name)
          session.execute ( "CREATE table {}_cuboids ( resolution int, zidx bigint, cuboid text, PRIMARY KEY ( resolution, zidx ) )".format(ch.channel_name), timeout=30)
        #session.execute( "CREATE table exceptions ( resolution int, zidx bigint, annoid bigint, exceptions text, PRIMARY KEY ( resolution, zidx, annoid ) )", timeout=30)
        #session.execute("CREATE table indexes ( resolution int, annoid bigint, cuboids text, PRIMARY KEY ( resolution, annoid ) )", timeout=30)
      except Exception, e:
        ch.delete()
        logging.error("Failed to create table for channel {}".format(channel_name))
        raise NDWSError("Failed to create table for channel {}".format(channel_name))
      finally:
        session.shutdown()

    elif pr.kvengine == DYNAMODB:

      try:
        # connect to dynamo
        dynamodb = boto3.resource('dynamodb')
  
        ctable = dynamodb.create_table(
          # RBTODO add user name
          TableName='{}_{}'.format(pr.project_name,ch.channel_name),
          KeySchema=[
            {
              'AttributeName': 'cuboidkey',
              'KeyType': 'HASH'
            },
          ],
          AttributeDefinitions=[
            {
              'AttributeName': 'cuboidkey',
              'AttributeType': 'S'
            },
            {
              'AttributeName': 'cuboid',
              'AttributeType': 'B'
            },
          ],
          ProvisionedThroughput={
        	  'ReadCapacityUnits': 10,
		        'WriteCapacityUnits': 10
          },
        )

        itable = dynamodb.create_table(
          TableName='{}_{}_idx'.format(pr.project_name,ch.channel_name),
          KeySchema=[
            {
              'AttributeName': 'idxkey',
              'KeyType': 'HASH'
            },
          ],
          AttributeDefinitions=[
            {
              'AttributeName': 'idxkey',
              'AttributeType': 'S'
            },
            {
              'AttributeName': 'idx',
              'AttributeType': 'B'
            },
          ],
          ProvisionedThroughput={
		        'ReadCapacityUnits': 10,
		        'WriteCapacityUnits': 10
          },
        )
  
        etable = dynamodb.create_table(
          TableName='{}_{}_exc'.format(pr.project_name,ch.channel_name),
          KeySchema=[
            {
              'AttributeName': 'exckey',
              'KeyType': 'HASH'
            },
          ],
          AttributeDefinitions=[
            {
              'AttributeName': 'exckey',
              'AttributeType': 'S'
            },
            {
              'AttributeName': 'exc',
              'AttributeType': 'B'
            },
          ],
          ProvisionedThroughput={
  		      'ReadCapacityUnits': 10,
		        'WriteCapacityUnits': 10
          },
        )
  
        # wait for the tables to exist
        ctable.meta.client.get_waiter('table_exists').wait(TableName='{}_{}'.format(pr.project_name,ch.channel_name))
        itable.meta.client.get_waiter('table_exists').wait(TableName='{}_{}_idx'.format(pr.project_name,ch.channel_name))
        etable.meta.client.get_waiter('table_exists').wait(TableName='{}_{}_exc'.format(pr.project_name,ch.channel_name))
      
      except Exception, e:
        import pdb; pdb.set_trace()
    
    elif pr.kvengine == REDIS:
      # Do nothing
      pass

    else:
      logging.error ("Unknown KV Engine requested: {}".format("RBTODO get name"))
      raise NDWSError ("Unknown KV Engine requested: {}".format("RBTODO get name"))


  def deleteNDDB (self, project_name):

    pr = Project.objects.get(project_name = project_name)

    if pr.kvengine == MYSQL:
      with closing(MySQLdb.connect (host = pr.host, user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'])) as conn:
        with closing(conn.cursor()) as cursor:
        # delete the database
          sql = "DROP DATABASE {}".format(pr.project_name)

          try:
            cursor.execute(sql)
            conn.commit()
          except MySQLdb.Error, e:
            # Skipping the error if the database does not exist
            if e.args[0] == 1008:
              logger.warning("Database {} does not exist".format(pr.project_name))
              pass
            else:
              conn.rollback()
              logger.error ("Failed to drop project database {}: {}. sql={}".format(e.args[0], e.args[1], sql))
              raise NDWSError ("Failed to drop project database {}: {}. sql={}".format(e.args[0], e.args[1], sql))


    elif pr.kvengine == CASSANDRA:
      try:
        cluster = Cluster( [pr.kvserver] )
        session = cluster.connect()
        session.execute ( "DROP KEYSPACE {}".format(pr.project_name), timeout=30 )
      except Exception, e:
        logger.warning("Keyspace {} does not exist".format(pr.project_name))
        pass
      finally:
        cluster.shutdown()

    elif pr.kvengine == RIAK:
      # connect to Riak
      rcli = riak.RiakClient(host=proj.kvserver, pb_port=8087, protocol='pbc')
      bucket = rcli.bucket_type("nd{}".format(proj.getProjectType())).bucket(proj.getDBName())

      key_list = rcli.get_keys(bucket)

      for k in key_list:
        bucket.delete(k)

    elif pr.kvengine == DYNAMODB:

      # connect to dynamo
      dynamodb = boto3.resource('dynamodb')

      # iterate over all the possible tables.  No name space delete.
      pr = NDProject(proj)
      chs = Channel.objects.filter(project_id=pr)
      for ch in chs:
        self.deleteNDChannel ( proj, ch.channel_name )
    
    elif pr.kvengine == REDIS:

      # Do nothing
      pass


  def deleteNDChannel (self, proj, channel_name):
    """Delete the tables for this channel"""

    pr = NDProject(proj)
    ch = NDChannel(pr, channel_name)
    table_list = []


    if pr.getKVEngine() == MYSQL:

      if ch.getChannelType() in ANNOTATION_CHANNELS:
        table_list.append(ch.getIdsTable())
        for key in annotation.anno_dbtables.keys():
          table_list.append(ch.getAnnoTable(key))

      for i in pr.datasetcfg.getResolutions():
        table_list.append(ch.getTable(i))
        if ch.getChannelType() in ANNOTATION_CHANNELS:
          table_list = table_list + [ch.getIdxTable(i), ch.getExceptionsTable(i)]

      try:
        conn = MySQLdb.connect (host = pr.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = pr.getProjectName() ) 
        # delete the tables for this channel
        sql = "DROP TABLES IF EXISTS {}".format(','.join(table_list))
      
        with closing(conn.cursor()) as cursor:
          cursor.execute (sql)
          conn.commit()
      except MySQLdb.Error, e:
        # Skipping the error if the table does not exist
        if e.args[0] == 1051:
          pass
        if e.args[0] == 1049:
          pass
        else:
          conn.rollback()
          logger.error ("Failed to drop channel tables {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise NDWSError ("Failed to drop channel tables {}: {}. sql={}".format(e.args[0], e.args[1], sql))
      
    elif pr.getKVEngine() == CASSANDRA:
      # KL TODO
      pass
    
    elif pr.getKVEngine() == RIAK:
      # KL TODO
      pass

    elif pr.getKVEngine() == DYNAMODB:

      import pdb; pdb.set_trace()
      dynamodb = boto3.resource('dynamodb')
      table_list = [ '{}_{}'.format(pr.getProjectName(),ch.getChannelName()),\
                     '{}_{}_idx'.format(pr.getProjectName(),ch.getChannelName()),\
                     '{}_{}_exc'.format(pr.getProjectName(),ch.getChannelName()) ]
      for tbl in table_list:
        try:
          table = dynamodb.Table(tbl)
          table.delete()
        except Exception, e:
          import pdb; pdb.set_trace()
          raise

    elif pr.getKVEngine() == REDIS:
      
      # Do nothing
      pass
      

  def loadDatasetConfig ( self, dataset ):
    """Query the database for the dataset information and build a db configuration"""
    return NDDataset (dataset)

  def loadToken ( self, token ):
    """Query django configuration for a token to bind to a project"""
    return NDProject (token)

  def getPublic ( self ):
    """ Return a list of public tokens """

    tkns = Token.objects.filter(public = PUBLIC_TRUE)
    return [t.token_name for t in tkns]
