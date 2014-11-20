# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
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


# RBTODO cuboids upload.  batch i/o with getcubes when possible

import numpy as np
import cStringIO
import zlib
import MySQLdb
import re
from collections import defaultdict
import itertools
from contextlib import closing

import zindex
import anncube
import imagecube
import ocpcaproj
import annotation
import annindex
import imagecube
import probmapcube
import ocpcachannel
import ocplib
import tempfile
import h5py

from ocpcaerror import OCPCAError

from ocpca_cy import mergeCube_cy
from ocpca_cy import cubeLocs_cy

import logging
logger=logging.getLogger("ocp")

import sys

import mysqlkvio
try:
  import casskvio
except:
  pass
try:
  import riakkvio
except:
  pass


################################################################################
#
#  class: OCPCADB
#
#  Manipulate/create/read from the Morton-order cube store
#
################################################################################

class OCPCADB: 

  def __init__ (self, annoproj):
    """Connect with the brain databases"""

    self.datasetcfg = annoproj.datasetcfg 
    self.annoproj = annoproj

    # Are there exceptions?
    self.EXCEPT_FLAG = self.annoproj.getExceptions()
    self.KVENGINE = self.annoproj.getKVEngine()

    # Choose the I/O engine for key/value data
    if self.annoproj.getKVEngine() == 'MySQL':
      import mysqlkvio
      self.kvio = mysqlkvio.MySQLKVIO(self)
      self.NPZ = True
    elif self.annoproj.getKVEngine() == 'Riak':
      import riakkvio
      self.kvio = riakkvio.RiakKVIO(self)
      self.NPZ = False
    elif self.annoproj.getKVEngine() == 'Cassandra':
      import casskvio
      self.kvio = casskvio.CassandraKVIO(self)
      self.NPZ = False
    else:
      raise OCPCAError ("Unknown key/value store.  Engine = {}".format(self.annoproj.getKVEngine()))

    # How many slices?
    [ self.startslice, endslice ] = self.datasetcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # Connection info for the metadata
    try:
      self.conn = MySQLdb.connect (host = self.annoproj.getDBHost(),
                            user = self.annoproj.getDBUser(),
                            passwd = self.annoproj.getDBPasswd(),
                            db = self.annoproj.getDBName())

      # start with no cursor
      self.cursor = None

    except MySQLdb.Error, e:
      self.conn = None
      logger.error("Failed to connect to database: %s, %s" % (self.annoproj.getDBHost(), self.annoproj.getDBName()))
      raise

    # create annidx object
    if (self.annoproj.getDBType()==ocpcaproj.ANNOTATIONS):
      self.annoIdx = annindex.AnnotateIndex ( self.kvio, self.annoproj )

  def close ( self ):
    """Close the connection"""
    if self.conn:
      self.conn.close()
    self.kvio.close()

#
#  Cursor handling routines.  We operate in two modes.  TxN at a time
#  
#

  def getCursor ( self ):
    """If we are in a transaction, return the cursor, otherwise make one"""

    if self.cursor == None:
      return self.conn.cursor()
    else:
      return self.cursor

  def closeCursor ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor == None:
      print "Cursor close"
      cursor.close()

  def closeCursorCommit ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor == None:
      print "Close and commit"
      self.conn.commit()
      cursor.close()


  def commit ( self ):
    """Commit the transaction.  Moved out of __del__ to make explicit.""" 

    self.cursor.close()
    self.conn.commit()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""

    self.cursor = self.conn.cursor()
    sql = "START TRANSACTION"
    self.cursor.execute ( sql )

  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""

    self.cursor.close()
    self.conn.rollback()


  #
  #  peekID
  #
  def peekID ( self ):
    """Look at the next ID but don't claim it.  This is an internal interface.
        It is not thread safe.  Need a way to lock the ids table for the 
        transaction to make it safe."""
    
    with closing ( self.conn.cursor() ) as cursor:

      # Query the current max identifier
      sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() )
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.warning ("Problem retrieving identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise

      # Here we've queried the highest id successfully    
      row = cursor.fetchone()
      # if the table is empty start at 1, 0 is no annotation
      if ( row[0] == None ):
        identifier = 1
      else:
        identifier = int ( row[0] ) + 1

      return identifier

  #
  #  nextIdentifier
  #
  def nextID ( self ):
    """Get an new identifier.
       This is it's own txn and should not be called inside another transaction. """


    with closing ( self.conn.cursor() ) as cursor:
    
      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES %s WRITE" % ( self.annoproj.getIDsTbl() )
      try:

        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() ) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 1
        else:
          identifier = int ( row[0] ) + 1

        # increment and update query
        sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(identifier) + " ) "
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

  #RBRM      self.conn.commit()

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier


  #
  #  setID
  # 
  #  Place the user selected id into the ids table
  #
  def setID ( self, annoid ):
    """Set a user specified identifier"""

    with closing ( self.conn.cursor() ) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES %s WRITE" % ( self.annoproj.getIDsTbl() )
      try:

        # try the insert, get ane exception if it doesn't work
        sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(annoid) + " ) "
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

#RBRM        self.conn.commit()

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoid


  #
  #  setBatchID
  # 
  #  Place the user selected id into the ids table
  #
  def setBatchID ( self, annoidList ):
    """ Set a user specified identifier """

    with closing ( self.conn.cursor() ) as cursor:


      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES %s WRITE" % ( self.annoproj.getIDsTbl() )
      try:

        # try the insert, get and if it doesn't work
        sql = "INSERT INTO {} VALUES ( %s ) ".format( str(self.annoproj.getIDsTbl()) )
        try:
          cursor.executemany ( sql, [str(i) for i in annoidList] )  
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoidList


  #
  #  reserve
  #
  def reserve ( self, count ):
    """Reserve contiguous identifiers.
       This is it's own txn and should not be called inside another transaction. """
    
    with closing ( self.conn.cursor() ) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES %s WRITE" % ( self.annoproj.getIDsTbl() )
      try:

        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() ) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 0
        else:
          identifier = int ( row[0] ) 

        # increment and update query
        sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(identifier+count) + " ) "
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise

      except Exception, e:
        logger.error ( "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier+1


  #
  # getCube
  #
  def getCube ( self, key, resolution, update=False ):
    """ Load a cube from the database """

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Create a cube object
    if (self.annoproj.getDBType()==ocpcaproj.ANNOTATIONS):
      cube = anncube.AnnotateCube ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.PROBMAP_32bit):
      cube = probmapcube.ProbMapCube32 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.IMAGES_8bit):
      cube = imagecube.ImageCube8 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.IMAGES_16bit):
      cube = imagecube.ImageCube16 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.RGB_32bit):
      cube = imagecube.ImageCube32 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.RGB_64bit):
      cube = imagecube.ImageCube64 ( cubedim )
    else:
      raise OCPCAError ("Unknown project type {}".format(self.annoproj.getDBType()))
  
    # get the block from the database
    cubestr = self.kvio.getCube ( key, resolution, update )

    if not cubestr:
      cube.zeros()
    else:
      # Handle the cube format here.  
      if self.NPZ:
          # decompress the cube
          cube.fromNPZ ( cubestr )

      else:
          # cubes are HDF5 files
          tmpfile = tempfile.NamedTemporaryFile ()
          tmpfile.write ( cubestr )
          tmpfile.seek(0)
          h5 = h5py.File ( tmpfile.name ) 

          # load the numpy array
          cube.data = np.array ( h5['cuboid'] )
          h5.close()
          tmpfile.close()

    return cube


  #
  # cputCube
  #  RBRM
  # cgetCube
  #
  def cgetCube ( self, key, resolution, update=False ):
    """Load a cube from the annotation database"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Create a cube object
    if (self.annoproj.getDBType()==ocpcaproj.ANNOTATIONS):
      cube = anncube.AnnotateCube ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.PROBMAP_32bit):
      cube = probmapcube.ProbMapCube32 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.IMAGES_8bit):
      cube = imagecube.ImageCube8 ( cubedim )
    elif (self.annoproj.getDBType()==ocpcaproj.IMAGES_16bit):
      cube = imagecube.ImageCube16 ( cubedim )
    else:
      raise OCPCAError ("Unknown project type {}".format(self.annoproj.getDBType()))
  
    # get the block from the database
    cubestr = self.ckvio.getCube ( key, resolution, update )

    # cubes are HDF5 files
    tmpfile = tempfile.NamedTemporaryFile ()
    tmpfile.write ( cubestr )
    tmpfile.seek(0)
    h5 = h5py.File ( tmpfile.name ) 

    # load the numpy array
    cube.data = np.array ( h5['cuboid'] )

    h5.close()
    tmpfile.close()

    return cube

  def cputCube ( self, zidx, resolution, cube ):
    """Store a cube in the annotation database"""

    # Handle the cube format here.  
    tmpfile= tempfile.NamedTemporaryFile ()
    h5 = h5py.File ( tmpfile.name )
    h5.create_dataset ( "cuboid", tuple(cube.data.shape), cube.data.dtype, compression='gzip',  data=cube.data )
    h5.close()
    tmpfile.seek(0)

    self.ckvio.putCube ( zidx, resolution, tmpfile.read(), not cube.fromZeros() )
    tmpfile.close()


  #
  # putCube
  #
  def putCube ( self, zidx, resolution, cube ):
    """Store a cube in the annotation database"""

    # Handle the cube format here.  
    if self.NPZ:
      self.kvio.putCube ( zidx, resolution, cube.toNPZ(), not cube.fromZeros() )
    else:
      tmpfile= tempfile.NamedTemporaryFile ()
      h5 = h5py.File ( tmpfile.name )
      h5.create_dataset ( "cuboid", tuple(cube.data.shape), cube.data.dtype, compression='gzip',  data=cube.data )
      h5.close()
      tmpfile.seek(0)

      self.kvio.putCube ( zidx, resolution, tmpfile.read(), not cube.fromZeros() )
      tmpfile.close()


  #
  # putBatchCube
  #
  def putBatchCube ( self, zidx, resolution, cube ):
    """Store a cube in the annotation database"""

    # Handle the cube format here.  
    if self.NPZ:
      self.kvio.putBatchCube ( zidx, resolution, cube.toNPZ(), not cube.fromZeros() )
    else:
      tmpfile= tempfile.NamedTemporaryFile ()
      h5 = h5py.File ( tmpfile.name )
      h5.create_dataset ( "cuboid", tuple(cube.data.shape), cube.data.dtype, compression='gzip',  data=cube.data )
      h5.close()
      tmpfile.seek(0)

      self.kvio.putBatchCube ( zidx, resolution, tmpfile.read(), not cube.fromZeros() )
      tmpfile.close()


  #
  # getExceptions
  #
  def getExceptions ( self, zidx, resolution, annoid ):
    """Load a cube from the annotation database"""

    excstr = self.kvio.getExceptions ( zidx, resolution, annoid )
    if excstr:
      if self.NPZ:
        return np.load(cStringIO.StringIO ( zlib.decompress(excstr)))
      else:
        # cubes are HDF5 files
        tmpfile = tempfile.NamedTemporaryFile ()
        tmpfile.write ( excstr )
        tmpfile.seek(0)
        h5 = h5py.File ( tmpfile.name ) 

        # load the numpy array
        excs = np.array ( h5['exceptions'] )
        h5.close()
        tmpfile.close()
        return excs
    else:
      return []


  #
  # updateExceptions
  #
  def updateExceptions ( self, key, resolution, exid, exceptions, update=False ):
    """Merge new exceptions with existing exceptions"""

    curexlist = self.getExceptions( key, resolution, exid ) 

    update = False

    if curexlist!=[]:
      oldexlist = [ ocplib.XYZMorton ( trpl ) for trpl in curexlist ]
      newexlist = [ ocplib.XYZMorton ( trpl ) for trpl in exceptions ]
      exlist = set(newexlist + oldexlist)
      exlist = [ ocplib.MortonXYZ ( zidx ) for zidx in exlist ]
      update = True
    else:
      exlist = exceptions

    self.putExceptions ( key, resolution, exid, exlist, update )


  def putExceptions ( self, key, resolution, exid, exceptions, update ):
    """Package the object and transact with kvio"""

    exceptions = np.array ( exceptions, dtype=np.uint32 )

    #RBMAYBE make exceptions zipped in a future incompatible version??
    if self.NPZ:
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, exceptions )
      excstr = fileobj.getvalue()
      self.kvio.putExceptions ( key, resolution, exid, excstr, update )
    else:
      tmpfile= tempfile.NamedTemporaryFile ()
      h5 = h5py.File ( tmpfile.name )
      h5.create_dataset ( "exceptions", tuple(exceptions.shape), exceptions.dtype,
                               compression='gzip',  data=exceptions )
      h5.close()
      tmpfile.seek(0)
      self.kvio.putExceptions ( key, resolution, exid, tmpfile.read(), update )
      tmpfile.close()


  #
  # removeExceptions
  #
  def removeExceptions ( self, key, resolution, entityid, exceptions ):
    """Remove a list of exceptions"""
    """Should be done in a transaction"""

    curexlist = self.getExceptions( key, resolution, entityid ) 

    if curexlist != []:

      oldexlist = set([ ocplib.XYZMorton ( trpl ) for trpl in curexlist ])
      newexlist = set([ ocplib.XYZMorton ( trpl ) for trpl in exceptions ])
      exlist = oldexlist-newexlist
      exlist = [ ocplib.MortonXYZ ( zidx ) for zidx in exlist ]

      self.putExceptions ( key, resolution, exid, exlist, True )


  #
  # queryRange
  #
  def queryRange ( self, lowkey, highkey, resolution ):
    """Create a stateful query to a range of values not including the high value.
         To be used with getNextCube().
         Not thread safe (context per object)
         Also, one cursor only.  Not at multiple resolutions"""

    self._qr_cursor = self.conn.cursor ()
    self._qr_resolution = resolution

    # get the block from the database
    sql = "SELECT zindex, cube FROM " + self.annoproj.getTable(resolution) + " WHERE zindex >= " + str(lowkey) + " AND zindex < " + str(highkey)

    try:
      self._qr_cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.error ( "Failed to retrieve data cube : %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise

  
  #
  # getNextCube
  #
  def getNextCube ( self ):
    """Retrieve the next cube in a queryRange.
         Not thread safe (context per object)"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ self._qr_resolution ] 

    # Create a cube object
    cube = anncube.AnnotateCube ( cubedim )

    row = self._qr_cursor.fetchone()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      cube.zeros ()
      self._qr_cursor.close()
      return [None,None]
    else: 
      # decompress the cube
      cube.fromNPZ ( row[1] )
      return [row[0],cube]

  #
  # getAllExceptions
  #
  def getAllExceptions ( self, key, resolution ):
    """Load all exceptions for this cube"""

    # get the block from the database
    cursor = self.getCursor()
    sql = "SELECT id, exlist FROM %s where zindex=%s" % ( 'exc'+str(resolution), key )
    try:
      cursor.execute ( sql )
      excrows = cursor.fetchall()
    except MySQLdb.Error, e:
      logger.error ( "Error reading exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor ( cursor )

    # Parse and unzip all of the exceptions    
    excs = []
    if excrows == None:
      return []
    else:
      for excstr in excrows:
        excs.append ((np.uint32(excstr[0]), np.load(cStringIO.StringIO(zlib.decompress(excstr[1])))))
      return excs



  #
  # annotate
  #
  #  number the voxels and build the exceptions
  #
  def annotate ( self, entityid, resolution, locations, conflictopt='O' ):
    """Label the voxel locations or add as exceptions is the are already labeled."""

    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    #  An item may exist across several cubes
    #  Convert the locations into Morton order

    # dictionary with the index
    cubeidx = defaultdict(set)

    # convert voxels z coordinate
    locations[:,2] = locations[:,2] - np.uint32(self.datasetcfg.slicerange[0])
    # RB  there was a bug here from conflicting types of locations (HDF5 array) and slicerange (L from MySQL query)
#    if max(locations[:,2]) > self.datasetcfg.slicerange[1]:
#      logger.error("Bad adjusted locations. Max z slice value {}".format(max(locations[:,2])))

    cubelocs = ocplib.locate_ctype ( np.array(locations, dtype=np.uint32), cubedim )
    #cubelocs = cubeLocs_cy ( np.array(locations, dtype=np.uint32), cubedim )

    # sort the arrary, by cubeloc
    cubelocs = ocplib.quicksort ( cubelocs )
    #cubelocs2.view('u4,u4,u4,u4').sort(order=['f0'], axis=0)

    # get the nonzero element offsets 
    nzdiff = np.r_[np.nonzero(np.diff(cubelocs[:,0]))]
    # then turn into a set of ranges of the same element
    listoffsets = np.r_[0, nzdiff + 1, len(cubelocs)]

    # start a transaction if supported
    self.kvio.startTxn()

    for i in range(len(listoffsets)-1):

      # grab the list of voxels for the first cube
      voxlist = cubelocs[listoffsets[i]:listoffsets[i+1],:][:,1:4]
      #  and the morton key
      key = cubelocs[listoffsets[i],0]

      cube = self.getCube ( key, resolution, True )

      # get a voxel offset for the cube
      cubeoff = ocplib.MortonXYZ( key )
      #cubeoff = zindex.MortonXYZ(key)
      offset = np.asarray([cubeoff[0]*cubedim[0],cubeoff[1]*cubedim[1],cubeoff[2]*cubedim[2]], dtype = np.uint32)

      # add the items
      exceptions = np.array(cube.annotate_ctype(entityid, offset, voxlist, conflictopt), dtype=np.uint8)
      #exceptions = np.array(cube.annotate(entityid, offset, voxlist, conflictopt), dtype=np.uint8)

      # update the sparse list of exceptions
      if self.EXCEPT_FLAG:
        if len(exceptions) != 0:
          self.updateExceptions ( key, resolution, entityid, exceptions )

      self.putCube ( key, resolution, cube)

      # add this cube to the index
      cubeidx[entityid].add(key)

    # write it to the database
    self.annoIdx.updateIndexDense(cubeidx,resolution)
    # commit cubes.  not commit controlled with metadata
    self.kvio.commit()


  #
  # putCubeSSD
  # 
  def putCubeSSD ( key, reolution, cube ):
    """ Write the cube to SSD's """
    print "HELLO"




  #
  # shave
  #
  #  reduce the voxels 
  #
  def shave ( self, entityid, resolution, locations ):
    """Label the voxel locations or add as exceptions is the are already labeled."""

    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # dictionary with the index
    cubeidx = defaultdict(set)

    # convert voxels z coordinate
    locations[:,2] = locations[:,2] - self.datasetcfg.slicerange[0]
    cubelocs = ocplib.locate_ctype ( np.array(locations, dtype=np.uint32), cubedim )
    #cubelocs2 = cubeLocs_cy ( np.array(locations, dtype=np.uint32), cubedim )

    # sort the arrary, by cubeloc
    cubelocs = ocplib.quicksort ( cubelocs )
    #cubelocs.view('u4,u4,u4,u4').sort(order=['f0'], axis=0)

    # get the nonzero element offsets 
    nzdiff = np.r_[np.nonzero(np.diff(cubelocs[:,0]))]
    # then turn into a set of ranges of the same element
    listoffsets = np.r_[0, nzdiff + 1, len(cubelocs)]

    self.kvio.startTxn()

    try:

      for i in range(len(listoffsets)-1):

        # grab the list of voxels for the first cube
        voxlist = cubelocs[listoffsets[i]:listoffsets[i+1],:][:,1:4]
        #  and the morton key
        key = cubelocs[listoffsets[i],0]

        cube = self.getCube ( key, resolution, True )

        # get a voxel offset for the cube
        cubeoff = ocplib.MortonXYZ(key)
        #cubeoff2 = zindex.MortonXYZ(key)
        offset = np.asarray( [cubeoff[0]*cubedim[0],cubeoff[1]*cubedim[1],cubeoff[2]*cubedim[2]], dtype=np.uint32 )

        # remove the items
        exlist, zeroed = cube.shave(entityid, offset, voxlist)
        # make sure that exceptions are stored as 8 bits
        exceptions = np.array(exlist, dtype=np.uint8)

        # update the sparse list of exceptions
        if self.EXCEPT_FLAG:
          if len(exceptions) != 0:
            self.kvio.removeExceptions ( key, resolution, entityid, exceptions )

        self.putCube ( key, resolution, cube)

        # For now do no index processing when shaving.  Assume there are still some
        #  voxels in the cube???

    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()


  #
  # annotateDense
  #
  #  Process a cube of data that has been labelled with annotations.
  #
  def annotateDense ( self, corner, resolution, annodata, conflictopt ):
    """Process all the annotations in the dense volume"""

    index_dict = defaultdict(set)

    # dim is in xyz, data is in zyxj
    dim = [ annodata.shape[2], annodata.shape[1], annodata.shape[0] ]

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    zoffset = corner[2]%zcubedim
    yoffset = corner[1]%ycubedim
    xoffset = corner[0]%xcubedim

    databuffer = np.zeros ([znumcubes*zcubedim, ynumcubes*ycubedim, xnumcubes*xcubedim], dtype=np.uint32 )
    databuffer [ zoffset:zoffset+dim[2], yoffset:yoffset+dim[1], xoffset:xoffset+dim[0] ] = annodata 

    # start a transaction if supported
    self.kvio.startTxn()

    try:

      for z in range(znumcubes):
        for y in range(ynumcubes):
          for x in range(xnumcubes):

            key = ocplib.XYZMorton ([x+xstart,y+ystart,z+zstart])
            cube = self.getCube ( key, resolution, True )

            if conflictopt == 'O':
              cube.overwrite ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            elif conflictopt == 'P':
              cube.preserve ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            elif conflictopt == 'E': 
              if self.EXCEPT_FLAG:
                exdata = cube.exception ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
                for exid in np.unique ( exdata ):
                  if exid != 0:
                    # get the offsets
                    exoffsets = np.nonzero ( exdata==exid )
                    # assemble into 3-tuples zyx->xyz
                    exceptions = np.array ( zip(exoffsets[2], exoffsets[1], exoffsets[0]), dtype=np.uint32 )
                    # update the exceptions
                    self.updateExceptions ( key, resolution, exid, exceptions )
                    # add to the index
                    index_dict[exid].add(key)
              else:
                logger.error("No exceptions for this project.")
                raise OCPCAError ( "No exceptions for this project.")
            else:
              logger.error ( "Unsupported conflict option %s" % conflictopt )
              raise OCPCAError ( "Unsupported conflict option %s" % conflictopt )

            self.putCube ( key, resolution, cube )

            #update the index for the cube
            # get the unique elements that are being added to the data

            uniqueels = np.unique ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            for el in uniqueels:
              index_dict[el].add(key) 

            # remove 0 no reason to index that
            if 0 in index_dict:
              del(index_dict[0])


      # Update all indexes
      self.annoIdx.updateIndexDense(index_dict,resolution)
      # commit cubes.  not commit controlled with metadata

    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()


  #
  #  Called when labeling an entity
  #
  def annotateEntityDense ( self, entityid, corner, resolution, annodata, conflictopt ):
    """Relabel all nonzero pixels to annotation id and call annotateDense"""

    vec_func = np.vectorize ( lambda x: 0 if x == 0 else entityid ) 
    annodata = vec_func ( annodata )
    return self.annotateDense ( corner, resolution, annodata, conflictopt )

  #
  # shaveDense
  #
  #  Reduce the specified annotations 
  #
  def shaveDense ( self, entityid, corner, resolution, annodata ):
    """Process all the annotations in the dense volume"""


    index_dict = defaultdict(set)

    # dim is in xyz, data is in zyxj
    dim = [ annodata.shape[2], annodata.shape[1], annodata.shape[0] ]

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    zoffset = corner[2]%zcubedim
    yoffset = corner[1]%ycubedim
    xoffset = corner[0]%xcubedim

    databuffer = np.zeros ([znumcubes*zcubedim, ynumcubes*ycubedim, xnumcubes*xcubedim], dtype=np.uint32 )
    databuffer [ zoffset:zoffset+dim[2], yoffset:yoffset+dim[1], xoffset:xoffset+dim[0] ] = annodata 

    # start a transaction if supported
    self.kvio.startTxn()

    try:

      for z in range(znumcubes):
        for y in range(ynumcubes):
          for x in range(xnumcubes):

            key = ocplib.XYZMorton ([x+xstart,y+ystart,z+zstart])
            cube = self.getCube ( key, resolution, True )

            exdata = cube.shaveDense ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            for exid in np.unique ( exdata ):
              if exid != 0:
                # get the offsets
                exoffsets = np.nonzero ( exdata==exid )
                # assemble into 3-tuples zyx->xyz
                exceptions = np.array ( zip(exoffsets[2], exoffsets[1], exoffsets[0]), dtype=np.uint32 )
                # update the exceptions
                self.kvio.removeExceptions ( key, resolution, exid, exceptions )
                # add to the index
                index_dict[exid].add(key)

            self.putCube ( key, resolution, cube)

            #update the index for the cube
            # get the unique elements that are being added to the data
            uniqueels = np.unique ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            for el in uniqueels:
              index_dict[el].add(key) 

            # remove 0 no reason to index that
            del(index_dict[0])

      # Update all indexes
      self.annoIdx.updateIndexDense(index_dict,resolution)

    except:
      self.kvio.rollback()
      raise

    # commit cubes.  not commit controlled with metadata
    self.kvio.commit()


  #
  # shaveEntityDense
  #
  #  Takes a bitmap for an entity and calls denseShave
  #  renumber the annotations to match the entity id.
  #
  def shaveEntityDense ( self, entityid, corner, resolution, annodata ):
    """Process all the annotations in the dense volume"""

    # Make shaving a per entity operation
    vec_func = np.vectorize ( lambda x: 0 if x == 0 else entityid ) 
    annodata = vec_func ( annodata )

    self.shaveDense ( entityid, corner, resolution, annodata )


  def _zoominCutout ( self, corner, dim, resolution ):
    """Scale to a smaller cutout that will be zoomed"""

    # scale the corner to lower resolution
    effcorner = corner[0]/(2**(self.annoproj.getResolution()-resolution)), corner[1]/(2**(self.annoproj.getResolution()-resolution)), corner[2]

    # pixels offset within big range
    xpixeloffset = corner[0]%(2**(self.annoproj.getResolution()-resolution))
    ypixeloffset = corner[1]%(2**(self.annoproj.getResolution()-resolution))

    # get the new dimension, snap up to power of 2
    outcorner = (corner[0]+dim[0],corner[1]+dim[1],corner[2]+dim[2])

    newoutcorner = (outcorner[0]-1)/(2**(self.annoproj.getResolution()-resolution))+1, (outcorner[1]-1)/(2**(self.annoproj.getResolution()-resolution))+1, outcorner[2]
    effdim = (newoutcorner[0]-effcorner[0],newoutcorner[1]-effcorner[1],newoutcorner[2]-effcorner[2])

    return effcorner, effdim, (xpixeloffset,ypixeloffset)


  def _zoomoutCutout ( self, corner, dim, resolution ):
    """Scale to a larger cutout that will be shrunk"""

    # scale the corner to higher resolution
    effcorner = corner[0]*(2**(resolution-self.annoproj.getResolution())), corner[1]*(2**(resolution-self.annoproj.getResolution())), corner[2]

    effdim = dim[0]*(2**(resolution-self.annoproj.getResolution())),dim[0]*(2**(resolution-self.annoproj.getResolution())),dim[2]

    return effcorner, effdim 

  #
  #  Return a cube of data from the database
  #  Must account for zeros.
  #
  def cutout ( self, corner, dim, resolution, channel=None, zscaling=None, annoids=None ):
    """Extract a cube of arbitrary size.  Need not be aligned."""

    # alter query if  (ocpcaproj)._resolution is > resolution
    # if cutout is below resolution, get a smaller cube and scaleup
    if self.annoproj.getDBType() in ocpcaproj.ANNOTATION_DATASETS and self.annoproj.getResolution() > resolution:

      #find the effective dimensions of the cutout (where the data is)
      effcorner, effdim, (xpixeloffset,ypixeloffset) = self._zoominCutout ( corner, dim, resolution )
      [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ self.annoproj.getResolution() ] 
      effresolution = self.annoproj.getResolution()

    # alter query if  (ocpcaproj)._resolution is < resolution
    # if cutout is above resolution, get a large cube and scaledown
    elif self.annoproj.getDBType() in ocpcaproj.ANNOTATION_DATASETS and self.annoproj.getResolution() < resolution and False:  #PYTODO self.annoproj.isPropagated() True needs to be a project dervied flag to specify is we have scaled or not 

      [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ self.annoproj.getResolution() ] 
      effcorner, effdim = self._zoomoutCutout ( corner, dim, resolution )
      effresolution = self.annoproj.getResolution()

    # this is the default path when not scaling up the resolution
    else:

      # get the size of the image and cube
      [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 
      effcorner = corner
      effdim = dim
      effresolution = resolution 

    # Round to the nearest larger cube in all dimensions
    zstart = effcorner[2]/zcubedim
    ystart = effcorner[1]/ycubedim
    xstart = effcorner[0]/xcubedim

    znumcubes = (effcorner[2]+effdim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (effcorner[1]+effdim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (effcorner[0]+effdim[0]+xcubedim-1)/xcubedim - xstart

    # RBTODO need to fix this for new I/O interface.  No dbname to getCubes
    # use the requested resolution
    if zscaling == 'isotropic':
      dbname = self.annoproj.getIsotropicTable(resolution)
    elif zscaling == 'nearisotropic' and self.datasetcfg.nearisoscaledown[resolution] > 1:
      dbname = self.annoproj.getNearIsoTable(resolution)
    else:
      dbname = self.annoproj.getTable(effresolution)

    if self.annoproj.getDBType() in ocpcaproj.ANNOTATION_DATASETS:

      # input cube is the database size
      incube = anncube.AnnotateCube ( cubedim )

      # output cube is as big as was asked for and zero it.
      outcube = anncube.AnnotateCube ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )
      outcube.zeros()

    elif self.annoproj.getDBType() in ocpcaproj.DATASETS_8bit:

      incube = imagecube.ImageCube8 ( cubedim )
      outcube = imagecube.ImageCube8 ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )

    elif self.annoproj.getDBType() in ocpcaproj.DATASETS_16bit:
      
      incube = imagecube.ImageCube16 ( cubedim )
      outcube = imagecube.ImageCube16 ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )

    elif (self.annoproj.getDBType() == ocpcaproj.RGB_32bit):

      incube = imagecube.ImageCube32 ( cubedim )
      outcube = imagecube.ImageCube32 ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )

    elif (self.annoproj.getDBType() == ocpcaproj.RGB_64bit):
    
      incube = imagecube.ImageCube64 ( cubedim )
      outcube = imagecube.ImageCube64 ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )
    
    elif (self.annoproj.getDBType() == ocpcaproj.PROBMAP_32bit):
      
      incube = probmapcube.ProbMapCube32 ( cubedim )
      outcube = probmapcube.ProbMapCube32 ( [xnumcubes*xcubedim,\
                                        ynumcubes*ycubedim,\
                                        znumcubes*zcubedim] )
                                        
    # Build a list of indexes to access
    listofidxs = []
    for z in range ( znumcubes ):
      for y in range ( ynumcubes ):
        for x in range ( xnumcubes ):
          mortonidx = ocplib.XYZMorton ( [x+xstart, y+ystart, z+zstart] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # xyz offset stored for later use
    lowxyz = ocplib.MortonXYZ ( listofidxs[0] )

    # Batch query for all cubes
    # Customize query to the database (include channel or not)
#    if (self.annoproj.getDBType() == ocpcaproj.CHANNELS_8bit or self.annoproj.getDBType() == ocpcaproj.CHANNELS_16bit):
#      # Convert channel as needed
#      channel = ocpcachannel.toID ( channel, self )
#      self.kvio.getChannelCubes(channel,listofidxs)
#
#    else:
    self.kvio.startTxn()

    try:

      if self.annoproj.getDBType() in ocpcaproj.CHANNEL_DATASETS:
        # Convert channel as needed
        channel = ocpcachannel.toID ( channel, self )
        cuboids = self.kvio.getChannelCubes(listofidxs,channel,effresolution)
      elif self.annoproj.getDBType() in ocpcaproj.TIMESERIES_DATASETS:
        cuboids = self.kvio.getTimeSeriesCubes(listofidxs,int(channel),effresolution)
      else:
        cuboids = self.kvio.getCubes(listofidxs,effresolution)
 
      # use the batch generator interface
      for idx, datastring in cuboids:

        #add the query result cube to the bigger cube
        curxyz = ocplib.MortonXYZ(int(idx))
        offset = [ curxyz[0]-lowxyz[0], curxyz[1]-lowxyz[1], curxyz[2]-lowxyz[2] ]

        if self.NPZ: 
          incube.fromNPZ ( datastring[:] )

          #RB testing
#          self.cputCube ( idx, resolution, incube )
#          newcube = self.cgetCube ( idx, resolution )

        else:
          # cubes are HDF5 files
          tmpfile = tempfile.NamedTemporaryFile ()
          tmpfile.write ( datastring )
          tmpfile.seek(0)
          h5 = h5py.File ( tmpfile.name ) 

          # load the numpy array
          incube.data = np.array ( h5['cuboid'] )

          h5.close()
          tmpfile.close()

        # apply exceptions if it's an annotation project
        if annoids!= None and self.annoproj.getDBType() == ocpcaproj.ANNOTATIONS:
          incube.data = ocplib.filter_ctype_OMP ( incube.data, annoids )
          self.applyCubeExceptions ( annoids, effresolution, idx, incube )

        # add it to the output cube
        outcube.addData ( incube, offset ) 

    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()

    # if we fetched a smaller cube to zoom, correct the result
    if self.annoproj.getDBType() in ocpcaproj.ANNOTATION_DATASETS and self.annoproj.getResolution() > resolution:

      outcube.zoomData ( self.annoproj.getResolution()-resolution )

      # need to trim based on the cube cutout at self.annoproj.getResolution()
      outcube.trim ( corner[0]%(xcubedim*(2**(self.annoproj.getResolution()-resolution)))+xpixeloffset,dim[0], corner[1]%(ycubedim*(2**(self.annoproj.getResolution()-resolution)))+ypixeloffset,dim[1], corner[2]%zcubedim,dim[2] )

    # if we fetch a larger cube, downscale it and correct
    elif self.annoproj.getDBType() in ocpcaproj.ANNOTATION_DATASETS and self.annoproj.getResolution() < resolution and False:  #RBTODO True needs to be a project dervied flag to specify is we have scaled or not 

      outcube.downScale ( resolution-self.annoproj.getResolution() )

      # need to trime based on the cube cutout at self.annoproj.getResolution()
      outcube.trim ( corner[0]%(xcubedim*(2**(self.annoproj.getResolution()-resolution))),dim[0], corner[1]%(ycubedim*(2**(self.annoproj.getResolution()-resolution))),dim[1], corner[2]%zcubedim,dim[2] )
      
    # need to trim down the array to size
    #  only if the dimensions are not the same
    elif dim[0] % xcubedim  == 0 and dim[1] % ycubedim  == 0 and dim[2] % zcubedim  == 0 and corner[0] % xcubedim  == 0 and corner[1] % ycubedim  == 0 and corner[2] % zcubedim  == 0:
      pass
    else:
      outcube.trim ( corner[0]%xcubedim,dim[0],corner[1]%ycubedim,dim[1],corner[2]%zcubedim,dim[2] )

    return outcube

  #
  # getVoxel -- return the identifier at a voxel
  #
  #
  def getVoxel ( self, resolution, voxel ):
    """Return the identifier at a voxel"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # convert the voxel into zindex and offsets
    # Round to the nearest larger cube in all dimensions
    xyzcube = [ voxel[0]/xcubedim, voxel[1]/ycubedim, (voxel[2]-self.startslice)/zcubedim ]
    xyzoffset =[ voxel[0]%xcubedim, voxel[1]%ycubedim, (voxel[2]-self.startslice)%zcubedim ]

    # Create a cube object
    cube = anncube.AnnotateCube ( cubedim )

    mortonidx = ocplib.XYZMorton ( xyzcube )

    #RBTODO write a test and fix for kvio

    cursor = self.getCursor()

    # get the block from the database
    sql = "SELECT cube FROM " + self.annoproj.getTable(resolution) + " WHERE zindex = " + str(mortonidx)
    try:
      cursor.execute ( sql )
      row=cursor.fetchone()
    except MySQLdb.Error, e:
      logger.warning ( "Error reading annotation data: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor(cursor)

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      retval = 0
    else: 
      cube.fromNPZ ( row[0] )
      retval = cube.getVoxel ( xyzoffset )

    return retval


  # Alternate to getVolume that returns a annocube
  def annoCutout ( self, annoids, resolution, corner, dim, remapid=None ):
    """Fetch a volume cutout with only the specified annotation"""

    # cutout is zoom aware
    cube = self.cutout(corner,dim,resolution, annoids=annoids )
  
    if remapid:
      vec_func = np.vectorize ( lambda x: np.uint32(remapid) if x != 0 else np.uint32(0) ) 
      cube.data = vec_func ( cube.data )

    return cube

  # helper function to apply exceptions
  def applyCubeExceptions ( self, annoids, resolution, idx, cube ):
    """Apply the expcetions to a specified cube and resolution"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 
  
    (x,y,z) = ocplib.MortonXYZ ( idx )

    # for the target ids
    for annoid in annoids:
      # apply exceptions
      exceptions = self.getExceptions( idx, resolution, annoid ) 
      for e in exceptions:
        cube.data[e[2],e[1],e[0]]=annoid

  #
  #  zoomVoxels
  #
  def zoomVoxels ( self, voxels, resgap ):
    """Convert voxels from one resolution to another based 
       on a positive number of hierarcy levels.
       This is used by both exception and the voxels data argument."""

    # correct for zoomed resolution
    newvoxels = []
    scaling = 2**(resgap)
    for vox in voxels:
      for numy in range(scaling):
        for numx in range(scaling):
          newvoxels.append ( (vox[0]*scaling + numx, vox[1]*scaling + numy, vox[2]) )
    return newvoxels


  #
  # getLocations -- return the list of locations associated with an identifier
  #
  def getLocations ( self, entityid, res ):

    # get the size of the image and cube
    resolution = int(res)
    
    #scale to project resolution
    if self.annoproj.getResolution() > resolution:
      effectiveres = self.annoproj.getResolution() 
    else:
      effectiveres = resolution


    voxlist = []

    zidxs = self.annoIdx.getIndex(entityid,effectiveres)
    if type(zidxs[0]) == np.float64:
      zidxs2 = self.annoIdx.getIndex(entityid,effectiveres)

    for zidx in zidxs:

      print zidx

      cb = self.getCube (zidx,effectiveres) 

      # mask out the entries that do not match the annotation id
      vec_func = np.vectorize ( lambda x: entityid if x == entityid else 0 )
      annodata = vec_func ( cb.data )
    
      # where are the entries
      offsets = np.nonzero ( annodata ) 
      voxels = np.array(zip(offsets[2], offsets[1], offsets[0]), dtype=np.uint32)

      # Get cube offset information
      [x,y,z] = ocplib.MortonXYZ(zidx)
      xoffset = x * self.datasetcfg.cubedim[resolution][0] 
      yoffset = y * self.datasetcfg.cubedim[resolution][1] 
      zoffset = z * self.datasetcfg.cubedim[resolution][2] + self.datasetcfg.slicerange[0]

      # Now add the exception voxels
      if self.EXCEPT_FLAG:
        exceptions = self.getExceptions( zidx, resolution, entityid ) 
        if exceptions != []:
          voxels = np.append ( voxels.flatten(), exceptions.flatten())
          voxels = voxels.reshape(len(voxels)/3,3)

      # Change the voxels back to image address space
      [ voxlist.append([a+xoffset, b+yoffset, c+zoffset]) for (a,b,c) in voxels ] 

    # zoom out the voxels if necessary 
    if effectiveres > resolution:
      voxlist = self.zoomVoxels ( voxlist, effectiveres-resolution )

    return voxlist


  #
  # getBoundingBox -- return a corner and dimension of the bounding box 
  #   for an annotation using the index.
  #
  def getBoundingBox ( self, annids, res ):
  
    # get the size of the image and cube
    resolution = int(res)

    # determine the resolution for project information
    if self.annoproj.getResolution() > resolution:
      effectiveres = self.annoproj.getResolution() 
      scaling = 2**(effectiveres-resolution)
    else:
      effectiveres = resolution
      scaling=1

    # all boxes in the indexes
    zidxs=[]
    for annid in annids:
      zidxs = itertools.chain(zidxs,self.annoIdx.getIndex(annid,effectiveres))
    
    # convert to xyz coordinates
    try:
      xyzvals = np.array ( [ ocplib.MortonXYZ(zidx) for zidx in zidxs ], dtype=np.uint32 )
    # if there's nothing in the chain, the array creation will fail
    except:
      return None, None

    cubedim = self.datasetcfg.cubedim [ resolution ] 

    # find the corners
    xmin = min(xyzvals[:,0]) * cubedim[0] * scaling
    xmax = (max(xyzvals[:,0])+1) * cubedim[0] * scaling
    ymin = min(xyzvals[:,1]) * cubedim[1] * scaling
    ymax = (max(xyzvals[:,1])+1) * cubedim[1] * scaling
    zmin = min(xyzvals[:,2]) * cubedim[2]
    zmax = (max(xyzvals[:,2])+1) * cubedim[2]

    corner = [ xmin, ymin, zmin+self.startslice ]
    dim = [ xmax-xmin, ymax-ymin, zmax-zmin ]

    return (corner,dim)


  def annoCubeOffsets ( self, dataids, resolution, remapid=False ):
    """an iterable on the offsets and cubes for an annotation"""
   
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # alter query if  (ocpcaproj)._resolution is > resolution
    # if cutout is below resolution, get a smaller cube and scaleup
    if self.annoproj.getResolution() > resolution:
      effectiveres = self.annoproj.getResolution() 
    else:
      effectiveres = resolution

    zidxs = set()
    for did in dataids:
      zidxs |= set ( self.annoIdx.getIndex(did,effectiveres))

    for zidx in zidxs:

      # get the cube and mask out the non annoid values
      cb = self.getCube (zidx,effectiveres) 
      if not remapid:
        cb.data = ocplib.filter_ctype_OMP ( cb.data, dataids )
      else: 
        cb.data = ocplib.filter_ctype_OMP ( cb.data, dataids )
        vec_func = np.vectorize ( lambda x: np.uint32(remapid) if x != 0 else np.uint32(0) ) 
        cb.data = vec_func ( cb.data )

      # zoom the data if not at the right resolution
      # and translate the zindex to the upper resolution
      (xoff,yoff,zoff) = ocplib.MortonXYZ ( zidx )
      offset = (xoff*xcubedim, yoff*ycubedim, zoff*zcubedim+self.startslice)

      # if we're zooming, so be it
      if resolution < effectiveres:
        cb.zoomData ( effectiveres-resolution )
        offset = (offset[0]*(2**(effectiveres-resolution)),offset[1]*(2**(effectiveres-resolution)),offset[2])

      # add any exceptions
      # Get exceptions if this DB supports it
      if self.EXCEPT_FLAG:
        for exid in dataids:
          exceptions = self.getExceptions( zidx, effectiveres, exid ) 
          if exceptions != []:
            if resolution < effectiveres:
                exceptions = self.zoomVoxels ( exceptions, effectiveres-resolution )
            # write as a loop first, then figure out how to optimize 
            # exceptions are stored relative to cube offset
            for e in exceptions:
              if not remapid:
                cb.data[e[2],e[1],e[0]]=exid
              else:
                cb.data[e[2],e[1],e[0]]=remapid

      yield (offset,cb.data)




  #
  # getAnnotation:  
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, id ):
    """Return a RAMON object by identifier"""

    cursor = self.getCursor()
    try:
      retval = annotation.getAnnotation( id, self, cursor )
    finally:
      self.closeCursor ( cursor ) 

    return retval

  #
  # putAnnotation:  
  #    store an HDF5 annotation to the database
  def putAnnotation ( self, anno, options='' ):
    """store an HDF5 annotation to the database"""
    
    cursor = self.getCursor()
    try:
      retval = annotation.putAnnotation( anno, self, cursor, options )
    except:
      self.closeCursor( cursor ) 
      raise

    self.closeCursorCommit(cursor)

    return retval

  #
  # deleteAnnotation:  
  #    remove an HDF5 annotation from the database
  def deleteAnnotation ( self, annoid, options='' ):
    """delete an HDF5 annotation from the database"""

    cursor = self.getCursor()
    try:
      retval = annotation.deleteAnnotation ( annoid, self, cursor, options )
      self.deleteAnnoData ( annoid )
    except:
      self.closeCursor( cursor ) 
      raise

    self.closeCursorCommit(cursor)
    
    return retval
  
  #
  #deleteAnnoData:
  #    Delete the voxel data from the database for annoid 
  #
  def deleteAnnoData ( self, annoid):

    resolutions = self.datasetcfg.resolutions

    self.kvio.startTxn()

    try:

      for res in resolutions:
      
        #get the cubes that contain the annotation
        zidxs = self.annoIdx.getIndex(annoid,res,True)
        
        #Delete annotation data
        for key in zidxs:
          cube = self.getCube ( key, res, True )
          vec_func = np.vectorize ( lambda x: 0 if x == annoid else x )
          cube.data = vec_func ( cube.data )
          # remove the expcetions
          if self.EXCEPT_FLAG:
            self.kvio.deleteExceptions ( key, res, annoid )
          self.putCube ( key, res, cube)
        
      # delete Index
      self.annoIdx.deleteIndex(annoid,resolutions)

    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()


  #
  # getChildren
  def getChildren ( self, annoid ):
    """get all the children of the annotation"""
 
    cursor = self.getCursor()
    try:
      retval = annotation.getChildren ( annoid, self, cursor )
    finally:
      self.closeCursor ( cursor )

    return retval

  
  # getAnnoObjects:  
  #    Return a list of annotation object IDs
  #  for now by type and status
  def getAnnoObjects ( self, args ):
    """Return a list of annotation object ids that match equality predicates.  
      Legal predicates are currently:
        type
        status
      Predicates are given in a dictionary.
    """

    # legal equality fields
    eqfields = ( 'type', 'status' )
    # legal comparative fields
    compfields = ( 'confidence' )

    # start of the SQL clause
    sql = "SELECT annoid FROM " + annotation.anno_dbtables['annotation'] 
    clause = ''
    limitclause = ""

    # iterate over the predicates
    it = iter(args)
    try: 

      field = it.next()

      # build a query for all the predicates
      while ( field ):

        # provide a limit clause for iterating through the database
        if field == "limit":
          val = it.next()
          if not re.match('^\d+$',val): 
            logger.warning ( "Limit needs an integer. Illegal value:%s" % (field,val) )
            raise OCPCAError ( "Limit needs an integer. Illegal value:%s" % (field,val) )

          limitclause = " LIMIT %s " % (val)

        # all other clauses
        else:
          if clause == '':
            clause += " WHERE "
          else:  
            clause += ' AND '

          if field in eqfields:
            val = it.next()
            if not re.match('^\w+$',val): 
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )

            clause += '%s = %s' % ( field, val )

          elif field in compfields:

            opstr = it.next()
            if opstr == 'lt':
              op = ' < '
            elif opstr == 'gt':
              op = ' > '
            else:
              logger.warning ( "Not a comparison operator: %s" % (opstr) )
              raise OCPCAError ( "Not a comparison operator: %s" % (opstr) )

            val = it.next()
            if not re.match('^[\d\.]+$',val): 
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )
            clause += '%s %s %s' % ( field, op, val )


          #RBTODO key/value fields?

          else:
            raise OCPCAError ( "Illegal field in URL: %s" % (field) )

        field = it.next()

    except StopIteration:
      pass
 

    sql += clause + limitclause + ';'

    cursor = self.getCursor()

    try:
      cursor.execute ( sql )
      annoids = np.array ( cursor.fetchall(), dtype=np.uint32 ).flatten()
    except MySQLdb.Error, e:
      logger.error ( "Error retrieving ids: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor( cursor )

    return np.array(annoids)


  #
  # writeCuboid
  #
  #  Write data that is not integral in cuboids
  #
  def writeCuboid ( self, corner, resolution, cuboiddata ):
    """Write an image through the Web service"""

    # dim is in xyz, data is in zyxj
    dim = [ cuboiddata.shape[2], cuboiddata.shape[1], cuboiddata.shape[0] ]

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    zoffset = corner[2]%zcubedim
    yoffset = corner[1]%ycubedim
    xoffset = corner[0]%xcubedim
    
    if self.annoproj.getDBType() == ocpcaproj.IMAGES_8bit:
      cuboiddtype = np.uint8  
    elif self.annoproj.getDBType() == ocpcaproj.IMAGES_16bit:
      cuboiddtype = np.uint16  
    elif self.annoproj.getDBType() == ocpcaproj.RGB_32bit:
      cuboiddtype = np.uint32
    elif self.annoproj.getDBType() == ocpcaproj.RGB_64bit:
      cuboiddtype = np.uint64
    elif self.annoproj.getDBType() == ocpcaproj.PROBMAP_32bit:
      cuboiddtype = np.float32

    databuffer = np.zeros ([znumcubes*zcubedim, ynumcubes*ycubedim, xnumcubes*xcubedim], dtype=cuboiddata.dtype )
    databuffer [ zoffset:zoffset+dim[2], yoffset:yoffset+dim[1], xoffset:xoffset+dim[0] ] = cuboiddata 

    self.kvio.startTxn()
 
    try:

      for z in range(znumcubes):
        for y in range(ynumcubes):
          for x in range(xnumcubes):

            key = ocplib.XYZMorton ([x+xstart,y+ystart,z+zstart])
     
            # probability maps have overwrite semantics
            cube = self.getCube ( key, resolution, True )
            cube.overwrite ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
            self.putCube ( key, resolution, cube)

    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()


  #
  # getChannels
  #
  #  query the channels and their identifiers
  #
  def getChannels ( self ):
    """query the channels and their identifiers"""

    cursor = self.getCursor()

    sql = 'SELECT * FROM channels';
    try:
      cursor.execute ( sql )
      chandict = dict(cursor.fetchall())
    except MySQLdb.Error, e:
      logger.warning ("Failed to query channels %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor(cursor)

    return chandict


  def mergeGlobal(self, ids, mergetype, res):
     # get the size of the image and cube
    resolution = int(res)
    # ID to merge annotations into 
    mergeid = ids[0]
 
    # PYTODO Check if this is a valid annotation that we are relabeling to
    if len(self.annoIdx.getIndex(int(mergeid),resolution)) == 0:
      raise OCPCAError(ids[0] + " not a valid annotation id")
  
    # Get the list of cubeindexes for the Ramon objects
    listofidxs = set()

    self.kvio.startTxn()
    try:

      # Do this for all ids. 
      for annid in ids:
        listofidxs = set(self.annoIdx.getIndex(annid,resolution))
        for key in listofidxs:
          cube = self.getCube (key,resolution)
          #Update exceptions if exception flag is set ( PJM added 03/31/14)
          if self.EXCEPT_FLAG:
            oldexlist = self.getExceptions( key, resolution, annid ) 
            self.kvio.deleteExceptions ( key, resolution, annid )
          
          # Cython optimized function  to relabel data from annid to mergeid
          mergeCube_cy (cube.data,mergeid,annid ) 
          self.putCube ( key, resolution,cube)
          
        # Delete annotation and all it's meta data from the database
        # except for the merge annotation
        if annid != mergeid:
          try:
            annotation.deleteAnnotation(annid,self,'')
          except:
            logger.warning("Failed to delete annotation {} during merge.".format(annid))


    except:
      self.kvio.rollback()
      raise

    self.kvio.commit()

    return "Merge complete"

  def merge2D(self, ids, mergetype, res,slicenum):
    # get the size of the image and cube
    resolution = int(res)
    print ids
    # PYTODO Check if this is a valid annotation that we are relabeling to
    if len(self.annoIdx.getIndex(ids[0],1)) == 0:
      raise OCPCAError(ids[0] + " not a valid annotation id")
    print mergetype
    listofidxs = set()
    for annid in ids[1:]:
      listofidxs |= set(self.annoIdx.getIndex(annid,resolution))

    return "Merge 2D"

  def merge3D(self, ids, corner, dim, res):
     # get the size of the image and cube
    resolution = int(res)
    dbname = self.annoproj.getTable(resolution)
# No emcaproj.  PYTODO fix this.
#    if (self.annoproj.getDBType() == emcaproj.ANNOTATIONS):
#      raise OCPCAError("The project is not  a Annotation project")
    
    # PYTODO Check if this is a valid annotation that we are relabelubg to
    if len(self.annoIdx.getIndex(ids[0],1)) == 0:
      raise OCPCAError(ids[0] + " not a valid annotation id")

    listofidxs = set()
    for annid in ids[1:]:
      listofidxs |= set(self.annoIdx.getIndex(annid,resolution))

      # Perform the cutout
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ]

    # Get the Cutout
    cube = self.cutout(corner,dim,resolution)    
    vec_func = np.vectorize ( lambda x: ids[0] if x in ids[1:] else x )
    cube.data = vec_func ( cube.data )

    self.annotateDense ( corner, resolution, cube )    

    # PYTODO - Relabel exceptions?????

    # Update Index and delete object?
    for annid in ids[1:]:
      #Wself.annoIdx.deleteIndex(annid,resolution)
      print "updateIndex"

    return "Merge 3D"


  def exceptionsCutout ( self, corner, dim, resolution ):
    """Return a list of exceptions in the specified region.
        Will return a np.array of shape x,y,z,id1,...,idn where n is the longest exception list"""
  
    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.datasetcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    dbname = self.annoproj.getTable(resolution)


    # Build a list of indexes to access                                                                                     
    listofidxs = []
    for z in range ( znumcubes ):
      for y in range ( ynumcubes ):
        for x in range ( xnumcubes ):
          mortonidx = ocplib.XYZMorton ( [x+xstart, y+ystart, z+zstart] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # generate list of ids for query
    sqllist = ', '.join(map(lambda x: str(x), listofidxs))
    sql = "SELECT zindex,id,exlist FROM exc{} WHERE zindex in ({})".format(resolution,sqllist)


    with closing ( self.conn.cursor() ) as func_cursor:

      # this query needs its own cursor
      try:
        func_cursor.execute(sql)
      except MySQLdb.Error, e:
        logger.warning ("Failed to query exceptions in cutout %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
        raise

      # data structure to hold list of exceptions
      excdict = defaultdict(set)

      prevzindex = None

      while ( True ):

        try: 
          cuboidzindex, annid, zexlist = func_cursor.fetchone()
        except:
          func_cursor.close()
          break

        # first row in a cuboid
        if np.uint32(cuboidzindex) != prevzindex:
          prevzindex = cuboidzindex
          # data for the current cube
          cube = self.getCube ( cuboidzindex, resolution )
          [ xcube, ycube, zcube ] = ocplib.MortonXYZ ( cuboidzindex )
          xcubeoff =xcube*xcubedim
          ycubeoff =ycube*ycubedim
          zcubeoff =zcube*zcubedim

        # accumulate entries
        # decompress the llist of exceptions
        fobj = cStringIO.StringIO ( zlib.decompress(zexlist) )
        exlist = np.load (fobj)

        for exc in exlist:
          excdict[(exc[0]+xcubeoff,exc[1]+ycubeoff,exc[2]+zcubeoff)].add(np.uint32(annid))
          # add voxel data 
          excdict[(exc[0]+xcubeoff,exc[1]+ycubeoff,exc[2]+zcubeoff)].add(cube.data[exc[2]%zcubedim,exc[1]%ycubedim,exc[0]%xcubedim])


    # Watch out for no exceptions
    if len(excdict) != 0:

      maxlist = max([ len(v) for (k,v) in excdict.iteritems() ])
      exoutput = np.zeros([len(excdict),maxlist+3], dtype=np.uint32)

      i=0
      for k,v in excdict.iteritems():
        l = len(v)
        exoutput[i,0:(l+3)] = [x for x in itertools.chain(k,v)]
        i+=1

    # Return None if there are no exceptions.
    else:
      exoutput = None

    return exoutput

