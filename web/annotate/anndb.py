import numpy as np
import cStringIO
import zlib
import MySQLdb
from collections import defaultdict

import zindex
import anncube
import annproj
import annotation
import annindex

from annerror import ANNError

import sys

################################################################################
#
#  class: AnnotateDB
#
#  Manipulate/create/read from the Morton-order cube store
#
################################################################################

#RBTODO needs to work out rollback


class AnnotateDB: 

  def __init__ (self, dbconf, annoproj):
    """Connect with the brain databases"""

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
      raise ANNError ( dbinfo )
      

    # How many slices?
    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # PYTODO create annidx object
    self.annoIdx = annindex.AnnotateIndex (dbconf,annoproj)

  def __del__ ( self ):
    """Close the connection"""
    self.conn.commit()
    self.conn.close()

  #
  #  peekID
  #
  def peekID ( self ):
    """What's the new identifier? Don't update.
       Not thread safe.  Don't use."""
    
    # Query the current max identifier
    cursor = self.conn.cursor ()
    sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Problem retrieving identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to create annotation identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
    # if the table is empty start at 1, 0 is no annotation
    if ( row[0] == None ):
      identifier = 1
    else:
      identifier = int ( row[0] ) + 1

    # increment and update query
    sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(identifier) + " ) "
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    return identifier

  #
  #  peekID
  #
  def peekID ( self ):
    """Look at the next ID but don't claim it.  This is an internal interface.
        It is not thread safe.  Need a way to lock the ids table for the 
        transaction to make it safe."""
    
    # Query the current max identifier
    cursor = self.conn.cursor ()
    sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Problem retrieving identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to create annotation identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
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
    """Get an new identifier"""
    
    # Query the current max identifier
    cursor = self.conn.cursor ()
    sql = "SELECT max(id) FROM " + str ( self.annoproj.getIDsTbl() )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Problem retrieving identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to create annotation identifier %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
    # if the table is empty start at 1, 0 is no annotation
    if ( row[0] == None ):
      identifier = 1
    else:
      identifier = int ( row[0] ) + 1

    # increment and update query
    sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(identifier) + " ) "
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    return identifier


  #
  #  setID
  # 
  #  Place the user selected id into the ids table
  #
  def setID ( self, annoid ):
    """Set a user specified identifier"""

    # try the insert, get ane exception if it doesn't work
    cursor = self.conn.cursor ()
    sql = "INSERT INTO " + str(self.annoproj.getIDsTbl()) + " VALUES ( " + str(annoid) + " ) "
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to insert into identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to set identifier table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    return annoid


  #
  # getCube
  #
  def getCube ( self, key, resolution ):
    """Load a cube from the annotation database"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ] 

    # Create a cube object
    cube = anncube.AnnotateCube ( cubedim )

    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT cube FROM " + self.annoproj.getTable(resolution) + " WHERE zindex = " + str(key)
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to retrieve data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    row = cursor.fetchone ()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      cube.zeros ()
    else: 
      # decompress the cube
      cube.fromNPZ ( row[0] )

    cursor.close()
     
    return cube


  #
  # putCube
  #
  def putCube ( self, key, resolution, cube ):
    """Store a cube from the annotation database"""

    cursor = self.conn.cursor ()

    # compress the cube
    npz = cube.toNPZ ()

    # we created a cube from zeros
    if cube.fromZeros ():

      sql = "INSERT INTO " + self.annoproj.getTable(resolution) +  "(zindex, cube) VALUES (%s, %s)"
      try:
        cursor.execute ( sql, (key,npz))
      except MySQLdb.Error, e:
        print "Error inserting cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        raise ANNError ( "Error inserting cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    else:

      sql = "UPDATE " + self.annoproj.getTable(resolution) + " SET cube=(%s) WHERE zindex=" + str(key)
      try:
        cursor.execute ( sql, (npz))
      except MySQLdb.Error, e:
        print "Error updating cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        raise ANNError ( "Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

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
      print "Failed to retrieve cube %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Failed to retrieve data cube : %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

  
  #
  # getNextCube
  #
  def getNextCube ( self ):
    """Retrieve the next cube in a queryRange.
         Not thread safe (context per object)"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ self._qr_resolution ] 

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
  # getExceptions
  #
  def getExceptions ( self, key, resolution, entityid ):
    """Load a the list of excpetions for this cube"""

    assert (0) # test/fix for resolutions

    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT exlist FROM " + self.except_tbl + " WHERE zindex = " + str(key) + " AND id = " + str(entityid)
    print sql 
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error reading exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    row = cursor.fetchone ()

    cursor.close()

    # If we can't find a list of exceptions, they don't exist
    if ( row == None ):
      return []
    else: 
      fobj = cStringIO.StringIO ( row[0] )
      return np.load ( fobj )

  #
  # updateExceptions
  #
  def updateExceptions ( self, key, resolution, entityid, exceptions ):
    """Store a list of exceptions"""

    assert (0) # test/fix for resolutions

    curexlist = self.getExceptions( key, entityid ) 

    print ("Current exceptions", curexlist )

    cursor = self.conn.cursor ()

    # RBTODO need to make exceptions a set
    if curexlist==[]:

      print "Adding new exceptions", exceptions 

      sql = "INSERT INTO " + self.except_tbl +  "(zindex, id, exlist) VALUES (%s, %s, %s)"
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, exceptions )
        print sql, key, entityid 
        cursor.execute ( sql, (key, entityid, fileobj.getvalue()))
      except MySQLdb.Error, e:
        print "Error inserting exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        raise ANNError ( "Error inserting exceptions: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
    # In this case we have an update query
    else:

      newexlist = np.append ( curexlist, exceptions )

      print newexlist

      print "Updating exceptions with ", exceptions 

      sql = "UPDATE " + self.except_tbl + " SET exlist=(%s) WHERE zindex=" + str(key) + " AND id = " + str(entityid)
      try:
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, newexlist )
        cursor.execute ( sql, (fileobj.getvalue()))
      except MySQLdb.Error, e:
        print "Error updating exceptions %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        assert 0

    cursor.close()


  #
  # annotate
  #
  #  number the voxels and build the exceptions
  #
  def annotate ( self, entityid, resolution, locations, conflictopt='O' ):
    """Label the voxel locations or add as exceptions is the are already labeled."""

    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ] 

    #  An item may exist across several cubes
    #  Convert the locations into Morton order

    # dictionary of mortonkeys
    cubelocs = defaultdict(list)
    
    # dictionary with the index
    cubeidx = defaultdict(set)

    #  list of locations inside each morton key
    for loc in locations:
      cubeno = loc[0]/cubedim[0], loc[1]/cubedim[1], (loc[2]-self.startslice)/cubedim[2]
      key = zindex.XYZMorton(cubeno)
      cubelocs[key].append([loc[0],loc[1],loc[2]-self.startslice])

    for key, loclist in cubelocs.iteritems():

      cube = self.getCube ( key, resolution )

      # get a voxel offset for the cube
      cubeoff = zindex.MortonXYZ(key)
      offset = [ cubeoff[0]*cubedim[0],\
                 cubeoff[1]*cubedim[1],\
                 cubeoff[2]*cubedim[2] ]

      # add the items
      exceptions = cube.annotate ( entityid, offset, loclist, conflictopt )

      # update the sparse list of exceptions
      if len(exceptions) != 0:
        self.updateExceptions ( key, entityid, exceptions )

      self.putCube ( key, resolution, cube)

      # add this cube to the index
      cubeidx[entityid].add(key)

    # write it to the database
    self.annoIdx.updateIndexDense(cubeidx,resolution)

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
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ] 

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
    for z in range(znumcubes):
      for y in range(ynumcubes):
        for x in range(xnumcubes):

          key = zindex.XYZMorton ([x+xstart,y+ystart,z+zstart])
          cube = self.getCube ( key, resolution )

          if conflictopt == 'O':
            cube.overwrite ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
          elif conflictopt == 'P':
            cube.preserve ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
          else:
            print "Unsupported conflict option.  FIX ME"
            assert 0

          self.putCube ( key, resolution, cube)

          #update the index for the cube
          # get the unique elements that are being added to the data
          uniqueels = np.unique ( databuffer [ z*zcubedim:(z+1)*zcubedim, y*ycubedim:(y+1)*ycubedim, x*xcubedim:(x+1)*xcubedim ] )
          # remove the 0 element
          for el in uniqueels:
            index_dict[el].add(key) 

          # remove 0 no reason to index that
          del(index_dict[0])

    # Update all indexes
    self.annoIdx.updateIndexDense(index_dict,resolution)

  #
  #  Called when labeling an entity
  #
  def annotateEntityDense ( self, entityid, corner, resolution, annodata, conflictopt ):
    """Relabel all nonzero pixels to annotation id and call annotateDense"""

    vec_func = np.vectorize ( lambda x: 0 if x == 0 else entityid ) 
    annodata = vec_func ( annodata )
    return self.annotateDense ( corner, resolution, annodata, conflictopt )


  #
  #  Return a cube of data from the database
  #  Must account for zeros.
  #
  def cutout ( self, corner, dim, resolution ):
    """Extract a cube of arbitrary size.  Need not be aligned."""
    
    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ] 

    # Round to the nearest larger cube in all dimensions
    zstart = corner[2]/zcubedim
    ystart = corner[1]/ycubedim
    xstart = corner[0]/xcubedim

    znumcubes = (corner[2]+dim[2]+zcubedim-1)/zcubedim - zstart
    ynumcubes = (corner[1]+dim[1]+ycubedim-1)/ycubedim - ystart
    xnumcubes = (corner[0]+dim[0]+xcubedim-1)/xcubedim - xstart

    # input cube is the database size
    incube = anncube.AnnotateCube ( cubedim )

    # output cube is as big as was asked for and zero it.
    outcube = anncube.AnnotateCube ( [xnumcubes*xcubedim,\
                                      ynumcubes*ycubedim,\
                                      znumcubes*zcubedim] )
    outcube.zeros()

    # Build a list of indexes to access
    listofidxs = []
    for z in range ( znumcubes ):
      for y in range ( ynumcubes ):
        for x in range ( xnumcubes ):
          mortonidx = zindex.XYZMorton ( [x+xstart, y+ystart, z+zstart] )
          listofidxs.append ( mortonidx )

    # Sort the indexes in Morton order
    listofidxs.sort()

    # Batch query for all cubes
    dbname = self.annoproj.getTable(resolution)
    cursor = self.conn.cursor()
    sql = "SELECT zindex, cube from " + dbname + " where zindex in (%s)" 
    # creats a %s for each list element
    in_p=', '.join(map(lambda x: '%s', listofidxs))
    # replace the single %s with the in_p string
    sql = sql % in_p
    rc = cursor.execute(sql, listofidxs)

    # xyz offset stored for later use
    lowxyz = zindex.MortonXYZ ( listofidxs[0] )

    # Get the objects and add to the cube
    while ( True ):

      try: 
        idx, datastring = cursor.fetchone()
      except:
        break

      #add the query result cube to the bigger cube
      curxyz = zindex.MortonXYZ(int(idx))
      offset = [ curxyz[0]-lowxyz[0], curxyz[1]-lowxyz[1], curxyz[2]-lowxyz[2] ]


      # get an input cube 
      incube.fromNPZ ( datastring[:] )

      # add it to the output cube
      outcube.addData ( incube, offset ) 


    # need to trim down the array to size
    #  only if the dimensions are not the same
    if dim[0] % xcubedim  == 0 and\
       dim[1] % ycubedim  == 0 and\
       dim[2] % zcubedim  == 0 and\
       corner[0] % xcubedim  == 0 and\
       corner[1] % ycubedim  == 0 and\
       corner[2] % zcubedim  == 0:
      pass
    else:
      outcube.trim ( corner[0]%xcubedim,dim[0],\
                      corner[1]%ycubedim,dim[1],\
                      corner[2]%zcubedim,dim[2] )

    return outcube


  #
  # getVoxel -- return the identifier at a voxel
  #
  #
  def getVoxel ( self, resolution, voxel ):
    """Return the identifier at a voxel"""

    # get the size of the image and cube
    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ] 

    # convert the voxel into zindex and offsets
    # Round to the nearest larger cube in all dimensions
    xyzcube = [ voxel[0]/xcubedim, voxel[1]/ycubedim, (voxel[2]-self.startslice)/zcubedim ]
    xyzoffset =[ voxel[0]%xcubedim, voxel[1]%ycubedim, (voxel[2]-self.startslice)%zcubedim ]

    # Create a cube object
    cube = anncube.AnnotateCube ( cubedim )

    mortonidx = zindex.XYZMorton ( xyzcube )

    cursor = self.conn.cursor ()

    # get the block from the database
    sql = "SELECT cube FROM " + self.annoproj.getTable(resolution) + " WHERE zindex = " + str(mortonidx)
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error reading annotation data: %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      assert 0

    row = cursor.fetchone ()

    # If we can't find a cube, assume it hasn't been written yet
    if ( row == None ):
      retval = 0
    else: 
      cube.fromNPZ ( row[0] )
      retval = cube.getVoxel ( xyzoffset )

    cursor.close()
     
    return retval


  #
  # getVolume -- return the volume associated with an identifier                                                                         
  # RB deprecated.  Use annoCutout instead. PYTODO
  def getVolume ( self, entityid, resolution, corner, dim ):
    cube = self.cutout( corner,dim,resolution)
    vec_func = np.vectorize ( lambda x: 0 if x != entityid else entityid ) 
    annodata = vec_func ( cube.data )
    return annodata

  # Alternate to getVolume that returns a annocube
  def annoCutout ( self, entityid, resolution, corner, dim ):
    """Fetch a volume cutout with only the specified annotation"""

    cube = self.cutout( corner,dim,resolution)
    vec_func = np.vectorize ( lambda x: 0 if x != entityid else entityid ) 
    cube.data = vec_func ( cube.data )
    return cube

  #
  # getLocations -- return the list of locations associated with an identifier
  #
  def getLocations ( self, entityid, res ):

    # get the size of the image and cube
    resolution = int(res)
    

#    [ xcubedim, ycubedim, zcubedim ] = cubedim = self.dbcfg.cubedim [ resolution ]
#
#    # get the index for the data                                                 
#    curIndex = self.annoIdx.getIndex(entityid,resolution)
#
#    #Retrieve the voxel list from the index
#    voxlist= []
#    for key in curIndex:
#      cube = self.getCube(key,resolution)
#            
#      cubeoff = zindex.MortonXYZ(key)
#      it = np.nditer ( cube.data, flags=['multi_index'])
#      
#      while not it.finished:
#        if (it[0] == entityid):
#          voxlist.append ( [ it.multi_index[2]+cubeoff[0]*cubedim[0],\
#                               it.multi_index[1]+ cubeoff[1]*cubedim[1],\
#                               it.multi_index[0]+ cubeoff[2]*cubedim[2] + self.startslice ])
#          
#        it.iternext()

    # alternate (faster) implementation
    #  use np.offsets and zip to reassmeble list.

    voxlist = []

    zidxs = self.annoIdx.getIndex(entityid,resolution)

    for zidx in zidxs:

      cb = self.getCube (zidx,resolution) 

      # mask out the entries that do not match the annotation id
      vec_func = np.vectorize ( lambda x: entityid if x == entityid else 0 )
      annodata = vec_func ( cb.data )
    
      # where are the entries
      offsets = np.nonzero ( annodata ) 
      voxels = zip ( offsets[2], offsets[1], offsets[0] ) 

      # Get cube offset information
      [x,y,z]=zindex.MortonXYZ(zidx)
      xoffset = x * self.dbcfg.cubedim[resolution][0] 
      yoffset = y * self.dbcfg.cubedim[resolution][1] 
      zoffset = z * self.dbcfg.cubedim[resolution][2] + self.dbcfg.slicerange[0]

      [ voxlist.append([a+xoffset, b+yoffset, c+zoffset]) for (a,b,c) in voxels ] 

    return voxlist


  #
  # getAnnotation:  
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, id ):
    """Return a RAMON object by identifier"""
    
    return annotation.getAnnotation( id, self )

  #
  # putAnnotation:  
  #    store an HDF5 annotation to the database
  def putAnnotation ( self, anno, options='' ):
    """store an HDF5 annotation to the database"""
    
    return annotation.putAnnotation( anno, self, options )


  # getAnnoObjects:  
  #    Return a list of annotation object IDs
  #  for now by type and status
  def getAnnoObjects ( self, predicates ):
    """Return a list of annotation object ids that match equality predicates.  
      Legal predicates are currently:
        type
        status
      Predicates are given in a dictionary.
    """

    # legal fields
    fields = ( 'type', 'status' )

    # start of the SQL clause
    sql = "SELECT annoid FROM " + annotation.anno_dbtables['annotation'] 

    clause = ''

    # probably need to avoid SQL injection attacks.
    #  throw an error or build the sql clause
    for field in predicates.keys():
      if field not in fields:
        raise ANNError ( "Illegal field in URL: %s" % (field) )
      elif clause == '':
        clause += " WHERE "
      else:  
        clause += ' AND '
      clause += '%s = %s' % ( field, predicates[field] )

    sql += clause + ';'

    cursor = self.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving ids. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving ids: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    annoids = cursor.fetchall()
    return np.array(annoids)

